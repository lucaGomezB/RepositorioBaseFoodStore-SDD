# Categoria model
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional


class Categoria(SQLModel, table=True):
    """Category model for products."""
    __tablename__ = "categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, index=True)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    parent_id: Optional[int] = Field(default=None, foreign_key="categorias.id")
    orden_display: int = Field(default=0)
    eliminado_en: Optional[str] = Field(default=None, max_length=50)
    fecha_creacion: Optional[str] = Field(default=None, max_length=50)
    fecha_actualizacion: Optional[str] = Field(default=None, max_length=50)

    # Self-referential relationship for hierarchy
    parent: Optional["Categoria"] = Relationship(
        back_populates="subcategorias",
        sa_relationship_kwargs={"remote_side": "Categoria.id"}
    )
    subcategorias: list["Categoria"] = Relationship(back_populates="parent")