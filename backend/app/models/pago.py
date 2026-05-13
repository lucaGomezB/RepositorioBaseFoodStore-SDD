# Pago model — MercadoPago payment tracking
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class Pago(SQLModel, table=True):
    """Payment record for MercadoPago transactions.

    Stores the complete lifecycle of a payment attempt, including
    the MercadoPago payment ID, status, and idempotency key to
    prevent duplicate charges (RN-PA02).

    Each Pedido can have multiple Pago records (retry attempts),
    but only one approved payment per order.
    """
    __tablename__ = "pagos"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False, index=True)
    mp_payment_id: Optional[str] = Field(default=None, max_length=100, unique=True, index=True)
    mp_status: str = Field(default="pending", max_length=30)
    external_reference: str = Field(max_length=100, unique=True, nullable=False)
    idempotency_key: str = Field(max_length=100, unique=True, nullable=False)
    card_token: Optional[str] = Field(default=None, max_length=255)
    status_detail: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    pedido: "Pedido" = Relationship(back_populates="pagos")
