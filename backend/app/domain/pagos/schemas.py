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
    model_config = {
        "json_schema_extra": {
            "example": {
                "pedido_id": 1,
                "card_token": "abc123def456",
                "payment_method_id": "visa",
            },
        },
    }


class PagoRead(BaseModel):
    """Response schema for payment data."""
    id: int
    pedido_id: int
    mp_payment_id: Optional[str] = None
    mp_status: str
    external_reference: str
    status_detail: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "pedido_id": 1,
                "mp_payment_id": "123456789",
                "mp_status": "approved",
                "external_reference": "food-store-1",
                "status_detail": "accredited",
                "created_at": "2024-01-15T10:35:00",
            },
        },
    }


class PagoWebhookRequest(BaseModel):
    """Schema for MercadoPago IPN webhook notification."""
    type: str  # "payment"
    data: dict  # {"id": "mp_payment_id"}
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "payment",
                "data": {"id": "123456789"},
            },
        },
    }


class PagoMockRequest(BaseModel):
    """Request schema for mock payment creation.

    No MercadoPago involved — the payment is immediately approved.
    """
    pedido_id: int
    model_config = {
        "json_schema_extra": {
            "example": {
                "pedido_id": 1,
            },
        },
    }


class PagoStatusResponse(BaseModel):
    """Simplified payment status response."""
    mp_status: str
    status_detail: Optional[str] = None
    mp_payment_id: Optional[str] = None
    external_reference: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "mp_status": "approved",
                "status_detail": "accredited",
                "mp_payment_id": "123456789",
                "external_reference": "food-store-1",
            },
        },
    }
