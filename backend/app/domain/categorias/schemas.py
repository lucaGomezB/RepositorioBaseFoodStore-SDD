# Categoria Schemas
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class CategoriaCreate(BaseModel):
    """Schema for creating a category."""
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    parent_id: Optional[int] = None
    orden_display: int = 0
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Hamburguesas",
                "descripcion": "Hamburguesas de carne vacuna y pollo",
                "parent_id": None,
                "orden_display": 1,
            },
        },
    }


class CategoriaUpdate(BaseModel):
    """Schema for updating a category."""
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    parent_id: Optional[int] = None
    orden_display: Optional[int] = None
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Hamburguesas Premium",
                "orden_display": 2,
            },
        },
    }


class CategoriaResponse(BaseModel):
    """Schema for category response (read)."""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None
    orden_display: int = 0
    eliminado_en: Optional[str] = None
    fecha_creacion: Optional[str] = None
    fecha_actualizacion: Optional[str] = None
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Hamburguesas",
                "descripcion": "Hamburguesas de carne vacuna y pollo",
                "parent_id": None,
                "orden_display": 1,
                "eliminado_en": None,
                "fecha_creacion": "2024-01-15T10:30:00",
            },
        },
    )


class CategoriaTree(BaseModel):
    """Schema for category tree with nested subcategories."""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None
    orden_display: int = 0
    subcategorias: List[CategoriaTree] = []
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "nombre": "Hamburguesas",
                "descripcion": "Hamburguesas de carne vacuna y pollo",
                "parent_id": None,
                "orden_display": 1,
                "subcategorias": [
                    {
                        "id": 2,
                        "nombre": "Hamburguesas de Pollo",
                        "descripcion": "Opciones de pollo",
                        "parent_id": 1,
                        "orden_display": 1,
                        "subcategorias": [],
                    },
                ],
            },
        },
    }
