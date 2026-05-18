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
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "admin@foodstore.com",
                "nombre": "Admin",
                "apellido": "User",
                "rol_id": 1,
                "activo": True,
                "fecha_creacion": "2024-01-15T10:30:00",
            },
        },
    )


class UsuarioUpdate(SQLModel):
    """Schema for updating a user. All fields optional."""
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    activo: Optional[bool] = None
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Admin",
                "apellido": "Updated",
                "activo": True,
            },
        },
    }


class UsuarioRoleUpdate(SQLModel):
    """Schema for updating a user's role assignment."""
    rol_id: int
    model_config = {
        "json_schema_extra": {
            "example": {
                "rol_id": 2,
            },
        },
    }
