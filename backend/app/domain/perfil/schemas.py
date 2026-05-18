# Perfil Schemas
from typing import Optional
from pydantic import ConfigDict, field_validator
from sqlmodel import SQLModel


class PerfilResponse(SQLModel):
    """Schema for reading user profile."""
    id: int
    email: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    fecha_creacion: str
    model_config = ConfigDict(from_attributes=True)


class PerfilUpdate(SQLModel):
    """Schema for updating user profile. All fields optional."""
    nombre: Optional[str] = None
    telefono: Optional[str] = None


class PasswordChange(SQLModel):
    """Schema for changing password."""
    password_actual: str
    password_nueva: str

    @field_validator("password_nueva")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v
