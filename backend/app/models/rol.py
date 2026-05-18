# Rol model
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

from app.models.usuario_rol import UsuarioRol

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Rol(SQLModel, table=True):
    """Table for user roles."""
    __tablename__ = "roles"

    id: int = Field(primary_key=True, default=1)
    nombre: str = Field(max_length=50, unique=True)
    descripcion: Optional[str] = Field(default=None, max_length=255)

    # Relationships
    users: list["Usuario"] = Relationship(
        back_populates="roles",
        link_model=UsuarioRol,
    )
