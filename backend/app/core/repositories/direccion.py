# Direccion Repository
from typing import List, Optional
from sqlmodel import Session, select
from app.core.repositories.base import BaseRepository
from app.models.direccion import Direccion


class DireccionRepository(BaseRepository[Direccion]):
    """Repository for Direccion model."""

    def __init__(self, session: Session):
        super().__init__(Direccion, session)

    def get_all_by_usuario(self, usuario_id: int) -> List[Direccion]:
        """Get all addresses for a specific user."""
        statement = select(Direccion).where(
            Direccion.usuario_id == usuario_id,
        ).order_by(Direccion.id)
        return list(self.session.exec(statement))

    def get_by_id_and_usuario(self, id: int, usuario_id: int) -> Optional[Direccion]:
        """Get an address by ID only if it belongs to the specified user."""
        statement = select(Direccion).where(
            Direccion.id == id,
            Direccion.usuario_id == usuario_id,
        )
        return self.session.exec(statement).first()
