# Pedido Schemas
from typing import Optional
from datetime import datetime
from pydantic import ConfigDict, field_validator
from sqlmodel import SQLModel


class ItemPedidoRequest(SQLModel):
    """Single item in an order creation request."""
    producto_id: int
    cantidad: int = 1
    exclusiones: list[int] = []

    @field_validator("cantidad")
    @classmethod
    def cantidad_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("cantidad must be >= 1")
        return v


class CrearPedidoRequest(SQLModel):
    """Schema for creating a new order."""
    items: list[ItemPedidoRequest]
    forma_pago_codigo: Optional[str] = None
    direccion_id: int

    @field_validator("items")
    @classmethod
    def must_have_at_least_one_item(cls, v: list) -> list:
        if not v:
            raise ValueError("At least one item is required")
        return v


class DetallePedidoRead(SQLModel):
    """Read schema for order line items (snapshot values)."""
    id: int
    producto_id: int
    nombre_snapshot: str
    precio_snapshot: float
    cantidad: int
    exclusiones: list[int]
    subtotal: float
    model_config = ConfigDict(from_attributes=True)


class HistorialEstadoRead(SQLModel):
    """Read schema for state transition history."""
    id: int
    estado_desde: Optional[str] = None
    estado_hacia: str
    motivo: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PedidoRead(SQLModel):
    """Compact read schema for order listings."""
    id: int
    usuario_id: int
    estado_codigo: str
    total: float
    costo_envio: float
    forma_pago_codigo: Optional[str] = None
    created_at: datetime
    items_count: int = 0
    usuario_nombre: Optional[str] = None
    usuario_email: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class PedidoListResponse(SQLModel):
    """Paginated response for order listings."""
    items: list[PedidoRead]
    total_count: int


class TransicionEstadoRequest(SQLModel):
    """Schema for transitioning an order's state."""
    nuevo_estado: str
    motivo: Optional[str] = None


class PedidoDetail(PedidoRead):
    """Detailed read schema with line items and history."""
    direccion_calle: str
    direccion_numero: str
    direccion_piso: Optional[str] = None
    direccion_ciudad: str
    direccion_cp: str
    detalles: list[DetallePedidoRead] = []
    historial_estados: list[HistorialEstadoRead] = []
    model_config = ConfigDict(from_attributes=True)


class AdminPedidoDetail(PedidoDetail):
    """Detailed read schema for admin with user contact info.

    Includes all PedidoDetail fields plus the user's email and phone
    for admin/order-management display.
    """
    usuario_email: str = ""
    usuario_telefono: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
