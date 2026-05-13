# Direccion Schemas
from typing import Optional
from datetime import datetime
from pydantic import ConfigDict
from sqlmodel import SQLModel


class DireccionBase(SQLModel):
    """Base schema for Direccion."""
    calle: str
    numero: str
    piso_depto: Optional[str] = None
    ciudad: str
    codigo_postal: str


class DireccionCreate(DireccionBase):
    """Schema for creating a direccion."""
    pass


class DireccionUpdate(SQLModel):
    """Schema for updating a direccion. All fields optional."""
    calle: Optional[str] = None
    numero: Optional[str] = None
    piso_depto: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None


class DireccionResponse(DireccionBase):
    """Schema for reading a direccion."""
    id: int
    usuario_id: int
    es_predeterminada: bool
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)
