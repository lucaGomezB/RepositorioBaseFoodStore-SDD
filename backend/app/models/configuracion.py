# Configuracion model — System configuration key-value store
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Configuracion(SQLModel, table=True):
    """System configuration key-value store.

    Stores operational parameters that admins can modify without
    touching code (US-060).
    """
    __tablename__ = "configuraciones"

    clave: str = Field(primary_key=True, max_length=100)
    valor: str = Field(max_length=500)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    updated_by: Optional[int] = Field(default=None, foreign_key="usuarios.id")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
