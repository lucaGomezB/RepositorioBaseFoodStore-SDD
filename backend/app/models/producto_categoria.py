# Link table: Producto - Categoria (many-to-many)
from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from typing import Optional


class ProductoCategoria(SQLModel, table=True):
    """Many-to-many relationship between Producto and Categoria."""
    __tablename__ = "producto_categoria"
    __table_args__ = (
        UniqueConstraint("producto_id", "categoria_id", name="uq_producto_categoria"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    producto_id: int = Field(foreign_key="productos.id", ondelete="CASCADE")
    categoria_id: int = Field(foreign_key="categorias.id", ondelete="CASCADE")
    es_principal: bool = Field(default=False)