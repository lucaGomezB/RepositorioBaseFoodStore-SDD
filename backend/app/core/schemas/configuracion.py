# Configuracion schemas — Pydantic v2
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConfigRead(BaseModel):
    """Response schema for a single configuration key-value."""
    clave: str
    valor: str
    descripcion: Optional[str] = None
    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ConfigUpdateItem(BaseModel):
    """Single item in a configuration update request."""
    clave: str
    valor: str


class ConfigUpdateRequest(BaseModel):
    """Request schema for updating multiple configurations."""
    configuraciones: list[ConfigUpdateItem]
