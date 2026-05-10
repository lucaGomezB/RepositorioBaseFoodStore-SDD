# EstadoPedido model
from sqlmodel import Field, SQLModel
from typing import Optional


class EstadoPedido(SQLModel, table=True):
    """Table for order states."""
    __tablename__ = "estado_pedido"

    id: int = Field(primary_key=True, default=1)
    nombre: str = Field(max_length=50, unique=True)
    descripcion: Optional[str] = Field(default=None, max_length=255)