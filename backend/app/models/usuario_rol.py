# UsuarioRol pivot table for M2M roles relationship
from sqlmodel import Field, SQLModel


class UsuarioRol(SQLModel, table=True):
    """Pivot table for user-role M2M relationship."""
    __tablename__ = "usuarios_roles"

    usuario_id: int = Field(
        foreign_key="usuarios.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    rol_id: int = Field(
        foreign_key="roles.id",
        primary_key=True,
        ondelete="CASCADE",
    )
