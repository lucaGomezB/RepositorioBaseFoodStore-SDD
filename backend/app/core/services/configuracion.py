# Configuracion Service
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.configuracion import Configuracion
from app.core.repositories.configuracion import ConfiguracionRepository


class ConfiguracionService:
    """Service for system configuration management."""

    @staticmethod
    def listar(session: Session) -> List[Configuracion]:
        """Get all configurations."""
        repo = ConfiguracionRepository(session)
        return repo.get_all()

    @staticmethod
    def actualizar(
        session: Session,
        items: list[dict],
        usuario_id: int,
    ) -> List[Configuracion]:
        """Update multiple configurations at once.

        Args:
            session: Database session.
            items: List of {clave, valor} dicts.
            usuario_id: ID of the admin performing the update.

        Returns:
            Updated list of all configurations.
        """
        repo = ConfiguracionRepository(session)
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

        session.commit()
        return repo.get_all()
