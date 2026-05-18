# Usuario model
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

from app.models.usuario_rol import UsuarioRol

if TYPE_CHECKING:
    from app.models.rol import Rol
    from app.models.direccion import Direccion
    from app.models.pedido import Pedido


class Usuario(SQLModel, table=True):
    """Table for users."""
    __tablename__ = "usuarios"

    id: int = Field(primary_key=True, default=None, nullable=False)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    activo: bool = Field(default=True)
    telefono: Optional[str] = Field(default=None, max_length=20)
    fecha_creacion: str = Field(default=None, max_length=50)
    fecha_actualizacion: str = Field(default=None, max_length=50)
    eliminado_en: Optional[datetime] = Field(default=None, nullable=True)

    # Relationships
    roles: list["Rol"] = Relationship(
        link_model=UsuarioRol,
        sa_relationship_kwargs={"lazy": "joined"},
    )
    direcciones: list["Direccion"] = Relationship(back_populates="usuario")
    pedidos: list["Pedido"] = Relationship(back_populates="usuario")

    @property
    def rol_id(self) -> int:
        """Get primary role ID (first role). For backward compatibility."""
        return self.roles[0].id if self.roles else 4

    @property
    def rol_ids(self) -> list[int]:
        """Get all role IDs."""
        return [r.id for r in self.roles]
