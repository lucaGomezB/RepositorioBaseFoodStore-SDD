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

    model_config = {
        "json_schema_extra": {
            "example": {
                "producto_id": 1,
                "cantidad": 2,
                "exclusiones": [3],
            },
        },
    }


class CrearPedidoRequest(SQLModel):
    """Schema for creating a new order."""
    items: list[ItemPedidoRequest]
    forma_pago_codigo: Optional[str] = None
    # Geolocation captured at payment
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    direccion_id: int

    @field_validator("items")
    @classmethod
    def must_have_at_least_one_item(cls, v: list) -> list:
        if not v:
            raise ValueError("At least one item is required")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {"producto_id": 1, "cantidad": 2, "exclusiones": []},
                    {"producto_id": 2, "cantidad": 1, "exclusiones": [3]},
                ],
                "forma_pago_codigo": "MERCADOPAGO",
                "direccion_id": 1,
            },
        },
    }


class DetallePedidoRead(SQLModel):
    """Read schema for order line items (snapshot values).
    Uses float for API serialization; DB stores Decimal for precision."""
    id: int
    producto_id: int
    nombre_snapshot: str
    precio_snapshot: float
    cantidad: int
    exclusiones: list[int]
    subtotal: float
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "producto_id": 1,
                "nombre_snapshot": "Hamburguesa Clasica",
                "precio_snapshot": 8.50,
                "cantidad": 2,
                "exclusiones": [],
                "subtotal": 17.00,
            },
        },
    )


class HistorialEstadoRead(SQLModel):
    """Read schema for state transition history."""
    id: int
    estado_desde: Optional[str] = None
    estado_hacia: str
    motivo: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "estado_desde": "PENDIENTE",
                "estado_hacia": "CONFIRMADO",
                "motivo": "Pago confirmado",
                "created_at": "2024-01-15T10:35:00",
            },
        },
    )


class PedidoRead(SQLModel):
    """Compact read schema for order listings.
    Uses float for API serialization; DB stores Decimal for precision."""
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
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "usuario_id": 1,
                "estado_codigo": "PENDIENTE",
                "total": 25.50,
                "costo_envio": 3.00,
                "forma_pago_codigo": "MERCADOPAGO",
                "created_at": "2024-01-15T10:30:00",
                "items_count": 3,
                "usuario_nombre": "Admin User",
                "usuario_email": "admin@foodstore.com",
            },
        },
    )


class PedidoListResponse(SQLModel):
    """Paginated response for order listings."""
    items: list[PedidoRead]
    total_count: int


class TransicionEstadoRequest(SQLModel):
    """Schema for transitioning an order's state."""
    nuevo_estado: str
    motivo: Optional[str] = None
    model_config = {
        "json_schema_extra": {
            "example": {
                "nuevo_estado": "CONFIRMADO",
                "motivo": "Pago verificado",
            },
        },
    }


class PedidoDetail(PedidoRead):
    """Detailed read schema with line items and history."""
    direccion_calle: str
    direccion_numero: str
    direccion_piso: Optional[str] = None
    direccion_ciudad: str
    direccion_cp: str
    # Geolocation captured at checkout
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    detalles: list[DetallePedidoRead] = []
    historial_estados: list[HistorialEstadoRead] = []
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "usuario_id": 1,
                "estado_codigo": "CONFIRMADO",
                "total": 25.50,
                "costo_envio": 3.00,
                "forma_pago_codigo": "MERCADOPAGO",
                "created_at": "2024-01-15T10:30:00",
                "items_count": 2,
                "direccion_calle": "Av. Siempre Viva",
                "direccion_numero": "742",
                "direccion_piso": "2A",
                "direccion_ciudad": "Springfield",
                "direccion_cp": "1234",
                "detalles": [
                    {
                        "id": 1,
                        "producto_id": 1,
                        "nombre_snapshot": "Hamburguesa Clasica",
                        "precio_snapshot": 8.50,
                        "cantidad": 2,
                        "exclusiones": [],
                        "subtotal": 17.00,
                    },
                ],
                "historial_estados": [
                    {
                        "id": 1,
                        "estado_desde": None,
                        "estado_hacia": "PENDIENTE",
                        "motivo": "Pedido creado",
                        "created_at": "2024-01-15T10:30:00",
                    },
                ],
            },
        },
    )


class AdminPedidoDetail(PedidoDetail):
    """Detailed read schema for admin with user contact info.

    Includes all PedidoDetail fields plus the user's email and phone
    for admin/order-management display.
    """
    usuario_email: str = ""
    usuario_telefono: Optional[str] = None
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "usuario_id": 1,
                "estado_codigo": "CONFIRMADO",
                "total": 25.50,
                "costo_envio": 3.00,
                "forma_pago_codigo": "MERCADOPAGO",
                "created_at": "2024-01-15T10:30:00",
                "items_count": 2,
                "direccion_calle": "Av. Siempre Viva",
                "direccion_numero": "742",
                "direccion_ciudad": "Springfield",
                "direccion_cp": "1234",
                "usuario_email": "cliente@example.com",
                "usuario_telefono": "555-1234",
                "detalles": [
                    {
                        "id": 1,
                        "producto_id": 1,
                        "nombre_snapshot": "Hamburguesa Clasica",
                        "precio_snapshot": 8.50,
                        "cantidad": 2,
                        "exclusiones": [],
                        "subtotal": 17.00,
                    },
                ],
                "historial_estados": [
                    {
                        "id": 1,
                        "estado_desde": None,
                        "estado_hacia": "PENDIENTE",
                        "motivo": "Pedido creado",
                        "created_at": "2024-01-15T10:30:00",
                    },
                ],
            },
        },
    )
