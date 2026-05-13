# HistorialEstadoPedido model (append-only audit trail)
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class HistorialEstadoPedido(SQLModel, table=True):
    """Append-only audit trail for order state transitions (RN-03).

    This table is INSERT-only. No UPDATE or DELETE operations are permitted.
    The first entry for an order always has estado_desde=NULL (RN-02).
    """
    __tablename__ = "historial_estados_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False)
    estado_desde: Optional[str] = Field(default=None, max_length=20)
    estado_hacia: str = Field(max_length=20)
    motivo: Optional[str] = Field(default=None, max_length=500)
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuarios.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    pedido: "Pedido" = Relationship(back_populates="historial_estados")
