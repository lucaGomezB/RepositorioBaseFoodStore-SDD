# Cocina Router — Kitchen Display System (REST + WebSocket)
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlmodel import Session

from app.core.database import get_db
from app.core.uow import UnitOfWork
from app.core.auth.deps import TokenPayload, get_current_user
from app.core.auth.authorization import require_roles
from app.core.auth.roles import Role
from app.core.auth.tokens import decode_token, verify_token_type
from app.core.websocket.manager import manager
from app.domain.cocina.service import CocinaService
from app.domain.cocina.schemas import PedidoCocinaListResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cocina", tags=["Cocina"])


# ---------------------------------------------------------------------------
# REST endpoint — initial load & polling fallback
# ---------------------------------------------------------------------------


@router.get("/pedidos", response_model=PedidoCocinaListResponse)
def listar_pedidos_cocina(
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(
        require_roles(Role.COCINA, Role.PEDIDOS, Role.ADMIN)
    ),
):
    """List all orders visible in the Kitchen Display System.

    Returns orders in CONFIRMADO and EN_PREPARACION states, ordered by
    age (oldest first). Each order includes the elapsed time since it
    entered the kitchen and the line items the kitchen team needs to
    prepare.

    Allowed roles: COCINA, PEDIDOS, ADMIN.
    """
    with UnitOfWork(session) as uow:
        return CocinaService.listar_pedidos(uow)


# ---------------------------------------------------------------------------
# WebSocket endpoint — real-time updates
# ---------------------------------------------------------------------------


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):
    """WebSocket endpoint for real-time KDS updates.

    **Authentication**
    The JWT access token is read from the ``access_token`` cookie which
    is sent automatically by the browser during the WebSocket handshake.
    Only users with ADMIN, PEDIDOS, or COCINA roles are allowed to connect.

    **Protocol**
    Once connected the server pushes JSON events for every relevant
    state transition (``PEDIDO_CONFIRMADO``, ``PEDIDO_EN_PREPARACION``,
    ``PEDIDO_EN_CAMINO``, ``PEDIDO_CANCELADO``).

    The client may send ``"ping"`` text messages to keep the connection
    alive; the server replies with ``{"type": "pong"}``.

    **Connection lifecycle**
    - On success: the connection is registered in the ``ConnectionManager``.
    - On disconnect or error: the connection is automatically unregistered.
    """
    # Validate JWT token from cookie --------------------------------------
    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=4001, reason="No auth token")
        return

    payload = decode_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    # Reject refresh tokens — only access tokens are valid for WS
    if not verify_token_type(token, "access"):
        await websocket.close(code=4001, reason="Invalid token type")
        return

    # Check role -----------------------------------------------------------
    user_roles: list[int] = payload.get("roles", [])
    allowed = {Role.ADMIN.value, Role.PEDIDOS.value, Role.COCINA.value}
    if not allowed.intersection(user_roles):
        await websocket.close(code=4003, reason="Insufficient permissions")
        return

    # Register connection and listen ---------------------------------------
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            # Future: handle other client messages here
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error (user %s): %s",
                     payload.get("user_id"), e)
        await manager.disconnect(websocket)
