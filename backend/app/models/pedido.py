# Pedido model
from decimal import Decimal
from sqlalchemy import Numeric
from sqlmodel import SQLModel, Field, Relationship, Column
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.estado_pedido import EstadoPedido
    from app.models.detalle_pedido import DetallePedido
    from app.models.historial_estado_pedido import HistorialEstadoPedido
    from app.models.pago import Pago


class Pedido(SQLModel, table=True):
    """Order model with address snapshots and FSM state tracking.

    Stores immutable snapshots of the delivery address at creation time
    to guarantee historical integrity (RN-PE01).
    """
    __tablename__ = "pedidos"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    estado_codigo: str = Field(foreign_key="estados_pedido.codigo", default="PENDIENTE")
    total: Decimal = Field(default=Decimal('0'), sa_column=Column(Numeric(10, 2)))
    costo_envio: Decimal = Field(default=Decimal('50.00'), sa_column=Column(Numeric(10, 2)))
    forma_pago_codigo: Optional[str] = Field(default=None, max_length=20)

    # Address snapshot at creation time (immutable)
    direccion_calle: str = Field(max_length=255)
    direccion_numero: str = Field(max_length=20)
    direccion_piso: Optional[str] = Field(default=None, max_length=50)
    direccion_ciudad: str = Field(max_length=100)
    direccion_cp: str = Field(max_length=20)

    # Geolocation (captured at checkout)
    latitud: Optional[float] = Field(default=None, nullable=True)
    longitud: Optional[float] = Field(default=None, nullable=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    usuario: "Usuario" = Relationship(back_populates="pedidos")
    estado: "EstadoPedido" = Relationship(back_populates="pedidos")
    detalles: list["DetallePedido"] = Relationship(back_populates="pedido")
    historial_estados: list["HistorialEstadoPedido"] = Relationship(back_populates="pedido")
    pagos: list["Pago"] = Relationship(back_populates="pedido")
