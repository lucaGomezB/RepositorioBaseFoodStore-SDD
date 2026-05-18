# Configuracion Service
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from fastapi import HTTPException, status

if TYPE_CHECKING:
    from app.core.uow import UnitOfWork

from app.models.configuracion import Configuracion
from app.domain.admin.repository import ConfiguracionRepository


class ConfiguracionService:
    """Service for system configuration management."""

    @staticmethod
    def listar(uow: "UnitOfWork") -> List[Configuracion]:
        """Get all configurations."""
        repo = ConfiguracionRepository(uow.session)
        return repo.get_all()

    @staticmethod
    def actualizar(
        uow: "UnitOfWork",
        items: list[dict],
        usuario_id: int,
    ) -> List[Configuracion]:
        """Update multiple configurations at once.

        Args:
            session: Database uow.session.
            items: List of {clave, valor} dicts.
            usuario_id: ID of the admin performing the update.

        Returns:
            Updated list of all configurations.
        """
        repo = ConfiguracionRepository(uow.session)
        now = datetime.now(timezone.utc)

        for item in items:
            clave = item.get("clave")
            valor = item.get("valor")

            # Validate key exists
            existing = repo.get_by_clave(clave)
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Configuración '{clave}' no encontrada",
                )

            existing.valor = valor
            existing.updated_by = usuario_id
            existing.updated_at = now
            repo.upsert(existing)

        return repo.get_all()
