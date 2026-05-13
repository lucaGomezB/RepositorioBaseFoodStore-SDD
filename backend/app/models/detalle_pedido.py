# DetallePedido model
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class DetallePedido(SQLModel, table=True):
    """Order line item with immutable product snapshots.

    Stores price and name at creation time so historical orders always
    reflect the original values regardless of later product updates (RN-04).
    """
    __tablename__ = "detalles_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False)
    producto_id: int = Field(foreign_key="productos.id", nullable=False)

    # Snapshots at creation time (immutable)
    nombre_snapshot: str = Field(max_length=255)
    precio_snapshot: float = Field(default=0)

    cantidad: int = Field(default=1)
    # IDs of removed ingredients (PostgreSQL INTEGER[])
    # Uses JSON for portability across PostgreSQL and SQLite.
    # On PostgreSQL this maps to JSON, on SQLite to TEXT.
    # Stores ingredient IDs that were removed from the item.
    exclusiones: list[int] = Field(default=[], sa_column=Column(JSON))
    subtotal: float = Field(default=0)

    # Relationship
    pedido: "Pedido" = Relationship(back_populates="detalles")
