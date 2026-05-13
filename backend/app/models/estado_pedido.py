# EstadoPedido model
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class EstadoPedido(SQLModel, table=True):
    """Order state catalog with FSM metadata.

    Uses VARCHAR semantic PK (PENDIENTE, CONFIRMADO, etc.) for readability
    in logs and debugging.
    """
    __tablename__ = "estados_pedido"

    codigo: str = Field(primary_key=True, max_length=20)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    orden: int = Field(default=0)
    es_terminal: bool = Field(default=False)

    pedidos: list["Pedido"] = Relationship(back_populates="estado")
