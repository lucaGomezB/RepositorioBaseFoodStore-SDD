# Pedido model
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.estado_pedido import EstadoPedido
    from app.models.detalle_pedido import DetallePedido
    from app.models.historial_estado_pedido import HistorialEstadoPedido


class Pedido(SQLModel, table=True):
    """Order model with address snapshots and FSM state tracking.

    Stores immutable snapshots of the delivery address at creation time
    to guarantee historical integrity (RN-PE01).
    """
    __tablename__ = "pedidos"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    estado_codigo: str = Field(foreign_key="estados_pedido.codigo", default="PENDIENTE")
    total: float = Field(default=0)
    costo_envio: float = Field(default=50.0)
    forma_pago_codigo: Optional[str] = Field(default=None, max_length=20)

    # Address snapshot at creation time (immutable)
    direccion_calle: str = Field(max_length=255)
    direccion_numero: str = Field(max_length=20)
    direccion_piso: Optional[str] = Field(default=None, max_length=50)
    direccion_ciudad: str = Field(max_length=100)
    direccion_cp: str = Field(max_length=20)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    usuario: "Usuario" = Relationship(back_populates="pedidos")
    estado: "EstadoPedido" = Relationship(back_populates="pedidos")
    detalles: list["DetallePedido"] = Relationship(back_populates="pedido")
    historial_estados: list["HistorialEstadoPedido"] = Relationship(back_populates="pedido")
