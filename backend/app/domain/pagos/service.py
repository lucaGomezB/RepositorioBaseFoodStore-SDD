# Pago Service — MercadoPago integration
import datetime
import hashlib
import hmac
import time
from typing import Optional, TYPE_CHECKING
from uuid import uuid4
from fastapi import HTTPException, status, Request

if TYPE_CHECKING:
    from app.core.uow import UnitOfWork

from app.core.config import settings
from app.domain.pagos.repository import PagoRepository
from app.domain.pedidos.repository import PedidoRepository
from app.domain.pedidos.service import PedidoService
from app.models.pago import Pago
from app.models.pedido import Pedido
from app.models.usuario import Usuario


class PagoService:
    """Service for MercadoPago payment operations.

    Handles payment creation via MercadoPago SDK, payment status
    queries, and IPN webhook processing with idempotency guarantees.
    """

    @staticmethod
    def _get_sdk():
        """Initialize and return the MercadoPago SDK."""
        import mercadopago
        return mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    # ------------------------------------------------------------------
    # Create payment
    # ------------------------------------------------------------------
    @staticmethod
    def crear_pago(
        uow: "UnitOfWork",
        pedido_id: int,
        usuario_id: int,
        card_token: Optional[str] = None,
        payment_method_id: Optional[str] = None,
    ) -> Pago:
        """Create a payment in MercadoPago and register it locally.

        Steps:
        1. Validate that the order exists and belongs to the user
        2. Validate the order is in PENDIENTE state
        3. Generate idempotency_key and check for duplicates
        4. Call MercadoPago API to create the payment
        5. Register the result in the Pago table

        Args:
            session: Unit of Work transaction wrapper.
            pedido_id: Order ID to pay for.
            usuario_id: Current user ID.
            card_token: Tokenized card from MercadoPago.js (optional).
            payment_method_id: Payment method identifier (optional).

        Returns:
            The created Pago record.

        Raises:
            HTTPException: 404 if order not found.
            HTTPException: 403 if order doesn't belong to user.
            HTTPException: 409 if order is not in PENDIENTE state.
        """
        repo = PagoRepository(uow.session)
        pedido_repo = PedidoRepository(uow.session)

        # Step 1: Validate order exists
        pedido = uow.session.get(Pedido, pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        # Step 1b: Ownership check
        if pedido.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        # Step 2: Validate order state
        if pedido.estado_codigo != "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El pedido no está en estado PENDIENTE (actual: {pedido.estado_codigo})",
            )

        # Step 3: Generate idempotency key
        idempotency_key = str(uuid4())
        external_reference = f"{pedido_id}-{idempotency_key[:8]}"  # Unique per attempt, links to order

        # Check for existing payment with same key (shouldn't happen with UUID4)
        existing = repo.get_by_idempotency_key(idempotency_key)
        if existing:
            return existing

        # Step 4: Call MercadoPago API
        sdk = PagoService._get_sdk()
        payment_data = {
            "transaction_amount": float(pedido.total),
            "description": f"Pedido FoodStore #{pedido_id}",
            "external_reference": external_reference,
            "idempotency_key": idempotency_key,
        }

        if card_token:
            payment_data["token"] = card_token
        if payment_method_id:
            payment_data["payment_method_id"] = payment_method_id

        # Default to simple integration if no card token
        if not card_token and not payment_method_id:
            # Basic checkout preference — redirects user to MP
            try:
                preference_data = {
                    "items": [
                        {
                            "title": f"Pedido FoodStore #{pedido_id}",
                            "quantity": 1,
                            "unit_price": float(pedido.total),
                            "currency_id": "ARS",
                        }
                    ],
                    "external_reference": external_reference,
                    "back_urls": {
                        "success": f"{settings.CORS_ORIGINS.split(',')[0].strip()}/pedidos/{pedido_id}",
                        "failure": f"{settings.CORS_ORIGINS.split(',')[0].strip()}/pedidos/{pedido_id}",
                        "pending": f"{settings.CORS_ORIGINS.split(',')[0].strip()}/pedidos/{pedido_id}",
                    },
                    "auto_return": "approved",
                    "notification_url": settings.MERCADOPAGO_WEBHOOK_SECRET and (
                        f"{settings.CORS_ORIGINS.split(',')[0].strip()}/api/v1/pagos/webhook"
                    ) or None,
                }
                preference_response = sdk.preference().create(preference_data)
                mp_result = preference_response.get("response", {})
                mp_payment_id = mp_result.get("id")
                mp_status = mp_result.get("status", "pending")
                status_detail = mp_result.get("status_detail")
                # Store preference URL for frontend redirect
                init_point = mp_result.get("init_point")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Error al crear preferencia en MercadoPago: {str(e)}",
                )
        else:
            # Direct payment with card token
            payment_data.update({
                "installments": 1,
                "payer": {"email": ""},  # Will be set from user data
            })

            try:
                payment_response = sdk.payment().create(payment_data)
                mp_result = payment_response.get("response", {})
                mp_payment_id = mp_result.get("id")
                mp_status = mp_result.get("status", "rejected")
                status_detail = mp_result.get("status_detail")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Error al procesar pago en MercadoPago: {str(e)}",
                )

        # Step 5: Register in Pago table
        pago = Pago(
            pedido_id=pedido_id,
            mp_payment_id=mp_payment_id,
            mp_status=mp_status or "pending",
            external_reference=external_reference,
            idempotency_key=idempotency_key,
            card_token=card_token,
            status_detail=status_detail,
        )
        uow.session.add(pago)
        uow.session.flush()
        uow.session.refresh(pago)
        return pago

    # ------------------------------------------------------------------
    # Get payment by order
    # ------------------------------------------------------------------
    @staticmethod
    def obtener_pago_por_pedido(
        uow: "UnitOfWork",
        pedido_id: int,
        usuario_id: int,
        is_admin: bool = False,
    ) -> Pago:
        """Get payment record for an order.

        Regular users can only see payments for their own orders.

        Args:
            session: Unit of Work transaction wrapper.
            pedido_id: Order ID.
            usuario_id: Current user ID.
            is_admin: Whether the user has admin role.

        Returns:
            The Pago record.

        Raises:
            HTTPException: 404 if not found or not authorized.
        """
        pedido = uow.session.get(Pedido, pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        if not is_admin and pedido.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        repo = PagoRepository(uow.session)
        pago = repo.get_by_pedido_id(pedido_id)
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron pagos para este pedido",
            )

        return pago

    # ------------------------------------------------------------------
    # Webhook signature verification
    # ------------------------------------------------------------------
    @staticmethod
    def verificar_firma_webhook(signature_header: Optional[str], raw_body: bytes):
        """Validate the X-Signature header from a MercadoPago webhook.

        MP signs webhooks with HMAC-SHA256 using the Webhook Secret:
          X-Signature: ts=<timestamp>,v1=<hmac>

        The HMAC is computed over: ts + "\\n" + raw_body
        Using MERCADOPAGO_WEBHOOK_SECRET as the key.

        Args:
            signature_header: Value of the X-Signature header.
            raw_body: Raw request body as bytes.

        Raises:
            HTTPException 403: If signature is missing or invalid.
        """
        webhook_secret = settings.MERCADOPAGO_WEBHOOK_SECRET
        if not webhook_secret:
            # If no secret configured, skip validation (dev mode)
            return

        if not signature_header:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Firma de webhook requerida",
            )

        # Parse the X-Signature header
        params = {}
        for part in signature_header.split(","):
            if "=" in part:
                key, value = part.split("=", 1)
                params[key.strip()] = value.strip()

        ts = params.get("ts")
        v1_signature = params.get("v1")

        if not ts or not v1_signature:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Formato de firma inválido",
            )

        # Check that timestamp is within 5 minutes
        try:
            request_time = int(ts)
            current_time = int(time.time())
            if abs(current_time - request_time) > 300:  # 5 minutes
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Firma expirada",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Timestamp inválido en firma",
            )

        # Compute expected signature
        message = f"{ts}\n".encode() + raw_body
        expected = hmac.new(
            key=webhook_secret.encode(),
            msg=message,
            digestmod=hashlib.sha256,
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(expected, v1_signature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Firma inválida",
            )

    # ------------------------------------------------------------------
    # Process webhook
    # ------------------------------------------------------------------
    @staticmethod
    def procesar_webhook(
        uow: "UnitOfWork",
        webhook_type: str,
        webhook_data: dict,
    ) -> dict:
        """Process a MercadoPago IPN webhook notification.

        Responds immediately (200) then processes asynchronously per
        RN-PA03. Verifies the payment status with MP API (RN-PA04).

        Args:
            session: Unit of Work transaction wrapper.
            webhook_type: Notification type ("payment").
            webhook_data: Notification data dict with "id" field.

        Returns:
            Dict with status message.

        Raises:
            HTTPException: 400 if webhook type is unsupported.
        """
        if webhook_type != "payment":
            # Acknowledge but ignore non-payment notifications
            return {"status": "ignored", "detail": f"Tipo no soportado: {webhook_type}"}

        mp_payment_id = webhook_data.get("id")
        if not mp_payment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falta mp_payment_id en la notificación",
            )

        # Query MP API for real payment status (RN-PA04)
        try:
            sdk = PagoService._get_sdk()
            mp_response = sdk.payment().get(mp_payment_id)
            mp_result = mp_response.get("response", {})
            mp_status = mp_result.get("status", "pending")
            status_detail = mp_result.get("status_detail")
            external_reference = mp_result.get("external_reference", "")
        except Exception:
            # If MP API fails, log and return — webhook will retry
            return {"status": "error", "detail": "Error al consultar MP API"}

        repo = PagoRepository(uow.session)

        # Find existing payment or create new one
        pago = repo.get_by_mp_payment_id(str(mp_payment_id))

        if not pago:
            # New payment notification — create record
            # Parse pedido_id from external_reference (format: "{pedido_id}-{uuid_prefix}")
            pedido_id_from_ref = int(external_reference.split("-")[0]) if external_reference and "-" in external_reference else 0
            pago = Pago(
                pedido_id=pedido_id_from_ref,
                mp_payment_id=str(mp_payment_id),
                mp_status=mp_status,
                external_reference=external_reference,
                idempotency_key=str(uuid4()),
                status_detail=status_detail,
            )
            uow.session.add(pago)
            uow.session.flush()
            uow.session.refresh(pago)
        else:
            # Existing payment — update status
            # Idempotency check: skip if same status (already processed)
            if pago.mp_status == mp_status:
                return {"status": "duplicate", "detail": "Notificación ya procesada"}

            pago.mp_status = mp_status
            pago.status_detail = status_detail
            pago.updated_at = datetime.datetime.now(datetime.UTC)

        # If approved, transition order to CONFIRMADO
        if mp_status == "approved" and pago.pedido_id:
            pedido = uow.session.get(Pedido, pago.pedido_id)
            if pedido and pedido.estado_codigo == "PENDIENTE":
                try:
                    PedidoService.transicionar_estado(
                        uow,
                        pago.pedido_id,
                        "CONFIRMADO",
                        usuario_id=None,  # System transition
                        motivo="Pago aprobado via MercadoPago",
                    )
                except Exception:
                    # Transition failed — don't break the webhook response
                    pass

        return {"status": "processed", "detail": f"Pago {mp_payment_id} actualizado a {mp_status}"}
