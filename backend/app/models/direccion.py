# Direccion model
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Direccion(SQLModel, table=True):
    """Delivery address model for users."""
    __tablename__ = "direcciones"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    calle: str = Field(max_length=255)
    numero: str = Field(max_length=20)
    piso_depto: Optional[str] = Field(default=None, max_length=50)
    ciudad: str = Field(max_length=100)
    codigo_postal: str = Field(max_length=20)
    latitud: Optional[float] = Field(default=None)
    longitud: Optional[float] = Field(default=None)
    es_predeterminada: bool = Field(default=False)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    usuario: Optional["Usuario"] = Relationship(back_populates="direcciones")
