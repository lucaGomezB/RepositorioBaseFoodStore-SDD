# Producto model
from datetime import datetime
from decimal import Decimal
from sqlmodel import Field, SQLModel, Column, Numeric
from typing import Optional


class Producto(SQLModel, table=True):
    """Product model."""
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150, index=True)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio_base: Decimal = Field(default=0, sa_column=Column(Numeric(precision=10, scale=2)))
    imagenes_url: Optional[str] = Field(default=None, max_length=1000)
    tiempo_prep_min: int = Field(default=0)
    stock_cantidad: int = Field(default=0)
    disponible: bool = Field(default=True)
    eliminado_en: Optional[datetime] = Field(default=None)
    fecha_creacion: Optional[str] = Field(default=None, max_length=50)
    fecha_actualizacion: Optional[str] = Field(default=None, max_length=50)

    # Note: Many-to-many relationships handled via repository methods
    # using ProductoCategoria and ProductoIngrediente tables