# Pago schemas — Pydantic v2
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PagoCreateRequest(BaseModel):
    """Request schema for creating a payment.

    The card_token is generated client-side by MercadoPago.js
    (PCI SAQ-A compliant — card data NEVER reaches our server).
    """
    pedido_id: int
    card_token: Optional[str] = None
    payment_method_id: Optional[str] = None


class PagoRead(BaseModel):
    """Response schema for payment data."""
    id: int
    pedido_id: int
    mp_payment_id: Optional[str] = None
    mp_status: str
    external_reference: str
    status_detail: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PagoWebhookRequest(BaseModel):
    """Schema for MercadoPago IPN webhook notification."""
    type: str  # "payment"
    data: dict  # {"id": "mp_payment_id"}


class PagoStatusResponse(BaseModel):
    """Simplified payment status response."""
    mp_status: str
    status_detail: Optional[str] = None
    mp_payment_id: Optional[str] = None
    external_reference: str
