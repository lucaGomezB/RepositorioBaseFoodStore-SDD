# Cocina Schemas — Kitchen Display System data contracts
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PedidoCocinaItem(BaseModel):
    """A single line item within a kitchen order card.

    Attributes:
        nombre_producto: Immutable snapshot of the product name at order time.
        cantidad: Quantity ordered.
        exclusiones: IDs of ingredients that were removed from this item.
        exclusiones_nombres: Human-readable names of excluded ingredients.
    """

    nombre_producto: str
    cantidad: int
    exclusiones: list[int] = []
    exclusiones_nombres: list[str] = []


class PedidoCocinaRead(BaseModel):
    """Kitchen display order representation.

    This is the schema returned by the KDS endpoint. It does **not**
    expose pricing or customer data — only what the kitchen team needs
    to prepare the order.

    Attributes:
        id: Database order ID.
        numero_pedido: Human-friendly order number (same as ``id`` in v1).
        estado_codigo: Current FSM state (CONFIRMADO or EN_PREPARACION).
        items: Line items to prepare.
        notas: Optional order-level notes (currently not stored server-side).
        tiempo_en_cocina_segundos: Seconds since the order entered CONFIRMADO.
        created_at: When the order was created.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_pedido: int
    estado_codigo: str
    items: list[PedidoCocinaItem]
    notas: Optional[str] = None
    tiempo_en_cocina_segundos: int = 0
    created_at: Optional[datetime] = None


class PedidoCocinaListResponse(BaseModel):
    """Paginated-style response for the KDS order list."""

    items: list[PedidoCocinaRead]
    total_count: int
