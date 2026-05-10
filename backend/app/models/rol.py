# Rol model
from sqlmodel import Field, SQLModel
from typing import Optional


class Rol(SQLModel, table=True):
    """Table for user roles."""
    __tablename__ = "roles"

    id: int = Field(primary_key=True, default=1)
    nombre: str = Field(max_length=50, unique=True)
    descripcion: Optional[str] = Field(default=None, max_length=255)