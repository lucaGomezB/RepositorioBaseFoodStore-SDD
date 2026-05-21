# Pagos Router — MercadoPago payment endpoints
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session

from app.core.database import get_db
from app.core.uow import UnitOfWork
from app.core.auth.deps import get_current_user, TokenPayload
from app.core.auth.authorization import require_roles
from app.core.auth.roles import Role
from app.domain.pagos.schemas import (
    PagoCreateRequest,
    PagoMockRequest,
    PagoRead,
)
from app.domain.pagos.service import PagoService
from app.domain.pedidos.service import _broadcast_event

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post("/crear", response_model=PagoRead, status_code=status.HTTP_201_CREATED)
def crear_pago(
    data: PagoCreateRequest,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """Create a payment for an order via MercadoPago.

    Validates the order exists, is in PENDIENTE state, belongs to the
    current user, and calls the MercadoPago API to process the payment.

    The card_token must be generated client-side via MercadoPago.js
    (PCI SAQ-A compliant — card data NEVER reaches our server).
    """
    try:
        with UnitOfWork(session) as uow:
            pago = PagoService.crear_pago(
                uow=uow,
                pedido_id=data.pedido_id,
                usuario_id=current_user.user_id,
                card_token=data.card_token,
                payment_method_id=data.payment_method_id,
            )
        return pago
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear pago: {str(e)}",
        )


@router.post("/mock", response_model=PagoRead, status_code=status.HTTP_201_CREATED)
def crear_pago_mock(
    data: PagoMockRequest,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """Create a mock payment for an order (no MercadoPago).

    Immediately approves the payment and transitions the order to
    CONFIRMADO. Useful for development/testing without real payments.
    """
    try:
        with UnitOfWork(session) as uow:
            pago = PagoService.crear_pago_mock(
                uow=uow,
                pedido_id=data.pedido_id,
                usuario_id=current_user.user_id,
            )
        # Broadcast after UoW commits successfully
        event = getattr(pago, '_pending_event', None)
        if event:
            _broadcast_event(event)
        return pago
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear pago mock: {str(e)}",
        )


@router.get("/{pedido_id}", response_model=PagoRead)
def obtener_pago(
    pedido_id: int,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    """Get payment status for an order.

    CLIENT users can only view their own orders' payments.
    ADMIN users can view any payment.
    """
    is_admin = current_user.rol_id == Role.ADMIN.value
    try:
        with UnitOfWork(session) as uow:
            pago = PagoService.obtener_pago_por_pedido(
                uow=uow,
                pedido_id=pedido_id,
                usuario_id=current_user.user_id,
                is_admin=is_admin,
            )
        return pago
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar pago: {str(e)}",
        )


@router.post("/webhook")
async def webhook_pago(
    request: Request,
    session: Session = Depends(get_db),
):
    """Receive MercadoPago IPN webhook notification.

    This endpoint is PUBLIC (no auth) by design — MercadoPago sends
    notifications without authentication. Security is handled via
    X-Signature validation.

    Responds 200 immediately per RN-PA03, then processes the
    notification asynchronously.
    """
    # Get raw body before any parsing (needed for signature verification)
    raw_body = await request.body()

    # Validate webhook signature
    signature_header = request.headers.get("x-signature")
    try:
        PagoService.verificar_firma_webhook(
            signature_header=signature_header,
            raw_body=raw_body,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Error al validar firma del webhook",
        )

    # Parse webhook data
    try:
        body = await request.json()
        webhook_type = body.get("type", "")
        webhook_data = body.get("data", {})

        with UnitOfWork(session) as uow:
            result = PagoService.procesar_webhook(
                uow=uow,
                webhook_type=webhook_type,
                webhook_data=webhook_data,
            )
        # Broadcast after UoW commits successfully
        event = result.pop("_pending_event", None) if isinstance(result, dict) else None
        if event:
            _broadcast_event(event)
        return result
    except Exception as e:
        # Always return 200 to prevent MercadoPago retries (RN-PE06)
        detail = e.detail if isinstance(e, HTTPException) else str(e)
        return {"status": "error", "detail": detail}
