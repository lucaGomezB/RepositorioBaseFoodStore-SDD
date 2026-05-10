# FormaPago model
from sqlmodel import Field, SQLModel
from typing import Optional


class FormaPago(SQLModel, table=True):
    """Table for payment methods."""
    __tablename__ = "forma_pago"

    id: int = Field(primary_key=True, default=1)
    nombre: str = Field(max_length=50, unique=True)
    descripcion: Optional[str] = Field(default=None, max_length=255)