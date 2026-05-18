# Ingrediente Service
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlmodel import select

if TYPE_CHECKING:
    from app.core.uow import UnitOfWork

from fastapi import HTTPException, status

from app.models.ingrediente import Ingrediente
from app.domain.ingredientes.repository import IngredienteRepository
from app.domain.ingredientes.schemas import IngredienteCreate, IngredienteUpdate


class IngredienteService:
    """Service for Ingrediente operations following Router -> Service -> Repository pattern."""

    def __init__(self, uow: "UnitOfWork", repo: Optional[IngredienteRepository] = None):
        self.uow = uow
        self.repo = repo or IngredienteRepository(uow.session)

    def get_all(self, es_alergeno: bool = None) -> list[Ingrediente]:
        """Get all ingredients, optionally filtered by es_alergeno. Excludes soft-deleted."""
        statement = select(Ingrediente).where(Ingrediente.eliminado_en.is_(None))

        if es_alergeno is not None:
            statement = statement.where(Ingrediente.es_alergeno == es_alergeno)

        statement = statement.order_by(Ingrediente.nombre)
        return list(self.uow.session.exec(statement))

    def get_by_id(self, ingrediente_id: int) -> Ingrediente:
        """Get a single ingredient by ID (excludes soft-deleted)."""
        ingrediente = self.repo.get(ingrediente_id)
        if not ingrediente or ingrediente.eliminado_en is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found",
            )
        return ingrediente

    def create(self, data: IngredienteCreate) -> Ingrediente:
        """Create a new ingredient with business validations."""
        # Validate nombre is unique
        existing = self.repo.get_by_name(data.nombre)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ingredient name already exists",
            )

        now = datetime.now(timezone.utc).isoformat()
        ingrediente = Ingrediente(
            nombre=data.nombre,
            descripcion=data.descripcion,
            es_alergeno=data.es_alergeno,
            fecha_creacion=now,
            fecha_actualizacion=now,
        )
        return self.repo.create(ingrediente)

    def update(self, ingrediente_id: int, data: IngredienteUpdate) -> Ingrediente:
        """Update an ingredient with validations (unique name)."""
        ingrediente = self.repo.get(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found",
            )

        update_data = data.model_dump(exclude_unset=True)

        # Validate nombre uniqueness if being changed
        if "nombre" in update_data:
            existing = self.repo.get_by_name(update_data["nombre"])
            if existing and existing.id != ingrediente_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ingredient name already exists",
                )

        update_data["fecha_actualizacion"] = datetime.now(timezone.utc).isoformat()

        updated = self.repo.update(ingrediente_id, update_data)
        self.uow.session.refresh(updated)
        return updated

    def soft_delete(self, ingrediente_id: int) -> Ingrediente:
        """Soft delete an ingredient by setting eliminado_en timestamp."""
        ingrediente = self.repo.get(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found",
            )

        now = datetime.now(timezone.utc).isoformat()
        updated = self.repo.update(ingrediente_id, {
            "eliminado_en": now,
            "fecha_actualizacion": now,
        })
        self.uow.session.refresh(updated)
        return updated
