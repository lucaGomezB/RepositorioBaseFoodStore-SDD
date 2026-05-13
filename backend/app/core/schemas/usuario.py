# Usuario Schemas for admin endpoints
from typing import Optional
from pydantic import ConfigDict
from sqlmodel import SQLModel


class UsuarioRead(SQLModel):
    """Schema for reading a user in admin context."""
    id: int
    email: str
    nombre: str
    apellido: str
    rol_id: int
    activo: bool
    fecha_creacion: str
    model_config = ConfigDict(from_attributes=True)


class UsuarioUpdate(SQLModel):
    """Schema for updating a user. All fields optional."""
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    activo: Optional[bool] = None


class UsuarioRoleUpdate(SQLModel):
    """Schema for updating a user's role assignment."""
    rol_id: int
