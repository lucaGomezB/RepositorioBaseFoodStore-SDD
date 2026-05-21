# Pedidos Router
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_db
from app.core.uow import UnitOfWork
from app.core.auth.deps import TokenPayload, get_current_user
from app.core.auth.authorization import require_roles
from app.core.auth.roles import Role
from app.domain.pedidos.schemas import (
    CrearPedidoRequest,
    PedidoRead,
    PedidoDetail,
    PedidoListResponse,
    HistorialEstadoRead,
    TransicionEstadoRequest,
)
from app.domain.pedidos.service import PedidoService, _broadcast_event

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    data: CrearPedidoRequest,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """Create a new order from the shopping cart.

    Validates stock, takes snapshots of prices and delivery address,
    calculates totals, and records the initial state transition — all
    within a single atomic transaction.

    Only CLIENT and ADMIN roles can create orders.
    """
    try:
        with UnitOfWork(session) as uow:
            pedido = PedidoService.crear_pedido(
                uow,
                current_user.user_id,
                data.model_dump(),
            )
            uow.session.refresh(pedido)
        return pedido
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{pedido_id}", response_model=PedidoDetail)
def obtener_pedido(
    pedido_id: int,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """Get order details with line items and state history.

    CLIENT users can only view their own orders.
    ADMIN users can view any order.
    """
    is_admin = current_user.rol_id == Role.ADMIN.value
    with UnitOfWork(session) as uow:
        pedido = PedidoService.obtener_pedido(
            uow, pedido_id, current_user.user_id, is_admin
        )

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    return pedido


@router.get("/{pedido_id}/historial", response_model=List[HistorialEstadoRead])
def read_pedido_historial(
    pedido_id: int,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Get the state transition history (audit trail) for an order.

    CLIENT users can only see history for their own orders.
    ADMIN users can see history for any order.

    Returns a chronologically ordered list of state transitions
    from the append-only audit log.
    """
    is_admin = current_user.rol_id == Role.ADMIN.value
    with UnitOfWork(session) as uow:
        return PedidoService.obtener_historial(
            uow,
            pedido_id,
            current_user.user_id,
            is_admin,
        )


@router.get("/", response_model=PedidoListResponse)
def listar_pedidos(
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN, Role.PEDIDOS)),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    estado: Optional[str] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    busqueda: Optional[str] = Query(None),
):
    """List orders with pagination and filters.

    CLIENT users see only their own orders (with optional estado filter).
    ADMIN/PEDIDOS users see all orders with advanced filters.

    Returns a paginated response with items and total_count.
    """
    is_admin_or_pedidos = current_user.rol_id in (Role.ADMIN.value, Role.PEDIDOS.value)

    with UnitOfWork(session) as uow:
        if is_admin_or_pedidos:
            items, total = PedidoService.listar_pedidos_admin(
                uow,
                estado=estado,
                desde=desde,
                hasta=hasta,
                busqueda=busqueda,
                skip=skip,
                limit=limit,
            )
        else:
            # CLIENT: only their own orders, basic estado filter
            items, total = PedidoService.listar_pedidos(
                uow,
                current_user.user_id,
                estado=estado,
                skip=skip,
                limit=limit,
            )

    return PedidoListResponse(items=items, total_count=total)


@router.patch("/{pedido_id}/estado", response_model=PedidoRead)
def transicionar_estado_pedido(
    pedido_id: int,
    data: TransicionEstadoRequest,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.PEDIDOS, Role.COCINA)),
):
    """Transition an order to a new state.

    Validates the transition against the FSM rules. If the transition is
    a cancellation from CONFIRMADO, stock is restored atomically.

    ADMIN, PEDIDOS and COCINA roles can transition orders.
    COCINA is limited to CONFIRMADO→EN_PREPARACION and EN_PREPARACION→EN_CAMINO
    (validated in the service layer per RN-CO03).
    """
    with UnitOfWork(session) as uow:
        pedido = PedidoService.transicionar_estado(
            uow, pedido_id, data.nuevo_estado,
            usuario_id=current_user.user_id, motivo=data.motivo,
            rol_id=current_user.rol_id,
        )
    # Broadcast after UoW commits successfully
    event = getattr(pedido, '_pending_event', None)
    if event:
        _broadcast_event(event)
    return pedido
