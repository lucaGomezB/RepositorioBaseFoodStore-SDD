# Direccion Schemas
from typing import Optional
from datetime import datetime
from pydantic import ConfigDict, field_validator
from sqlmodel import SQLModel


class DireccionBase(SQLModel):
    """Base schema for Direccion."""
    calle: str
    numero: str
    piso_depto: Optional[str] = None
    ciudad: str
    codigo_postal: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class DireccionCreate(DireccionBase):
    """Schema for creating a direccion."""

    @field_validator("latitud")
    @classmethod
    def validar_latitud(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitud debe estar entre -90 y 90")
        return v

    @field_validator("longitud")
    @classmethod
    def validar_longitud(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < -180 or v > 180):
            raise ValueError("Longitud debe estar entre -180 y 180")
        return v


class DireccionUpdate(SQLModel):
    """Schema for updating a direccion. All fields optional."""
    calle: Optional[str] = None
    numero: Optional[str] = None
    piso_depto: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

    @field_validator("latitud")
    @classmethod
    def validar_latitud(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitud debe estar entre -90 y 90")
        return v

    @field_validator("longitud")
    @classmethod
    def validar_longitud(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < -180 or v > 180):
            raise ValueError("Longitud debe estar entre -180 y 180")
        return v


class DireccionResponse(DireccionBase):
    """Schema for reading a direccion."""
    id: int
    usuario_id: int
    es_predeterminada: bool
    creado_en: datetime
    actualizado_en: datetime
    model_config = ConfigDict(from_attributes=True)
