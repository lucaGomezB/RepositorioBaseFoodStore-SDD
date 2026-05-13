# Link table: Producto - Ingrediente (many-to-many)
from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from typing import Optional


class ProductoIngrediente(SQLModel, table=True):
    """Many-to-many relationship between Producto and Ingrediente."""
    __tablename__ = "producto_ingrediente"
    __table_args__ = (
        UniqueConstraint("producto_id", "ingrediente_id", name="uq_producto_ingrediente"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    producto_id: int = Field(foreign_key="productos.id", ondelete="CASCADE")
    ingrediente_id: int = Field(foreign_key="ingredientes.id", ondelete="CASCADE")
    es_removible: bool = Field(default=True)
    es_principal: bool = Field(default=False)
    orden: int = Field(default=0)