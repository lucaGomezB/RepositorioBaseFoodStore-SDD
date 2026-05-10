# Usuario model
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.rol import Rol


class Usuario(SQLModel, table=True):
    """Table for users."""
    __tablename__ = "usuarios"

    id: int = Field(primary_key=True, default=None, nullable=False)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    rol_id: int = Field(foreign_key="roles.id", default=4)
    activo: bool = Field(default=True)
    fecha_creacion: str = Field(default=None, max_length=50)
    fecha_actualizacion: str = Field(default=None, max_length=50)

    # Relationship
    rol: "Rol" = Relationship(sa_relationship_kwargs={"lazy": "joined"})