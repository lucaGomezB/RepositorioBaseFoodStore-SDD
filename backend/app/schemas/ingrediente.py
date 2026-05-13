# Ingrediente Schemas
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class IngredienteCreate(BaseModel):
    """Schema for creating an ingredient."""
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    es_alergeno: bool = Field(default=False)


class IngredienteUpdate(BaseModel):
    """Schema for updating an ingredient."""
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    es_alergeno: Optional[bool] = None


class IngredienteResponse(BaseModel):
    """Schema for ingredient response (read)."""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: bool = False
    eliminado_en: Optional[str] = None
    fecha_creacion: Optional[str] = None
    fecha_actualizacion: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
