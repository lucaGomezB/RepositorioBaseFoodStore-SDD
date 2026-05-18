# Direccion Service
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.core.uow import UnitOfWork

from app.models.direccion import Direccion
from app.domain.direcciones.repository import DireccionRepository


class DireccionService:
    """Service for Direccion operations."""

    @staticmethod
    def crear(uow: "UnitOfWork", usuario_id: int, data: dict) -> Direccion:
        """Create a new address.

        If this is the user's first address, it is auto-marked as default (RN-DI01).
        """
        repo = DireccionRepository(uow.session)

        # Check if user has any existing addresses
        existing = repo.get_all_by_usuario(usuario_id)
        is_first = len(existing) == 0

        now = datetime.now(timezone.utc)
        direccion_data = {
            **data,
            "usuario_id": usuario_id,
            "es_predeterminada": is_first,
            "creado_en": now,
            "actualizado_en": now,
        }

        direccion = Direccion(**direccion_data)
        return repo.create(direccion)

    @staticmethod
    def listar_por_usuario(uow: "UnitOfWork", usuario_id: int) -> List[Direccion]:
        """List all addresses for a user."""
        repo = DireccionRepository(uow.session)
        return repo.get_all_by_usuario(usuario_id)

    @staticmethod
    def actualizar(uow: "UnitOfWork", id: int, usuario_id: int, data: dict) -> Optional[Direccion]:
        """Update an address, validating ownership."""
        repo = DireccionRepository(uow.session)
        direccion = repo.get_by_id_and_usuario(id, usuario_id)
        if not direccion:
            return None

        # Update only provided fields
        values = {k: v for k, v in data.items() if v is not None}
        values["actualizado_en"] = datetime.now(timezone.utc)

        for key, value in values.items():
            if hasattr(direccion, key):
                setattr(direccion, key, value)

        uow.session.add(direccion)
        uow.session.flush()
        uow.session.refresh(direccion)
        return direccion

    @staticmethod
    def eliminar(uow: "UnitOfWork", id: int, usuario_id: int) -> bool:
        """Delete an address, validating ownership. Returns True if deleted."""
        repo = DireccionRepository(uow.session)
        direccion = repo.get_by_id_and_usuario(id, usuario_id)
        if not direccion:
            return False

        repo.delete(id)
        return True

    @staticmethod
    def marcar_predeterminada(uow: "UnitOfWork", id: int, usuario_id: int) -> Optional[Direccion]:
        """Set an address as default, atomically removing the flag from the previous one.

        Uses a transaction to ensure only one address is marked as default (RN-DI02).
        """
        repo = DireccionRepository(uow.session)
        direccion = repo.get_by_id_and_usuario(id, usuario_id)
        if not direccion:
            return None

        # Unset all default addresses for this user
        all_user_direcciones = repo.get_all_by_usuario(usuario_id)
        for d in all_user_direcciones:
            if d.es_predeterminada:
                d.es_predeterminada = False
                d.actualizado_en = datetime.now(timezone.utc)
                uow.session.add(d)

        # Set the chosen one
        direccion.es_predeterminada = True
        direccion.actualizado_en = datetime.now(timezone.utc)
        uow.session.add(direccion)

        uow.session.flush()
        uow.session.refresh(direccion)

        return direccion
