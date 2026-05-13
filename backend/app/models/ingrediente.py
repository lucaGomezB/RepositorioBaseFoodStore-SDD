# Ingrediente model
from sqlmodel import Field, SQLModel
from typing import Optional


class Ingrediente(SQLModel, table=True):
    """Ingredient model for products."""
    __tablename__ = "ingredientes"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, index=True)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    es_alergeno: bool = Field(default=False)
    eliminado_en: Optional[str] = Field(default=None, max_length=50)
    fecha_creacion: Optional[str] = Field(default=None, max_length=50)
    fecha_actualizacion: Optional[str] = Field(default=None, max_length=50)

    # Note: Many-to-many relationship handled via repository methods
    # using ProductoIngrediente table