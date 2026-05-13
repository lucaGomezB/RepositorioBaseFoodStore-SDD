# Usuario Repository
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select, func
from sqlalchemy import or_

from app.core.repositories.base import BaseRepository
from app.models.usuario import Usuario


class UsuarioRepository(BaseRepository[Usuario]):
    """Repository for Usuario model."""

    def __init__(self, session: Session):
        super().__init__(Usuario, session)

    def get_by_email(self, email: str) -> Usuario:
        """Get user by email."""
        return self.get_by_field("email", email)

    def get_active_users(self) -> list[Usuario]:
        """Get all active users (not soft-deleted)."""
        statement = select(Usuario).where(
            Usuario.activo.is_(True),
            Usuario.eliminado_en.is_(None),
        )
        return list(self.session.exec(statement))

    def get_by_rol(self, rol_id: int) -> list[Usuario]:
        """Get all users with a specific role (excluding soft-deleted)."""
        statement = select(Usuario).where(
            Usuario.rol_id == rol_id,
            Usuario.eliminado_en.is_(None),
        )
        return list(self.session.exec(statement))

    def get_paginated(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        rol_id: Optional[int] = None,
    ) -> tuple[list[Usuario], int]:
        """Get paginated users with optional search and role filter.

        Excludes soft-deleted users (eliminado_en IS NOT NULL).

        Args:
            skip: Number of records to skip (offset).
            limit: Max records to return.
            search: Optional text search on nombre, apellido, or email.
            rol_id: Optional role ID filter.

        Returns:
            Tuple of (list of Usuario, total count matching filters).
        """
        # Base: exclude soft-deleted
        conditions = [Usuario.eliminado_en.is_(None)]

        if search:
            like_pattern = f"%{search}%"
            conditions.append(
                or_(
                    Usuario.nombre.ilike(like_pattern),
                    Usuario.apellido.ilike(like_pattern),
                    Usuario.email.ilike(like_pattern),
                )
            )

        if rol_id is not None:
            conditions.append(Usuario.rol_id == rol_id)

        # Count total matching records
        count_stmt = select(func.count(Usuario.id)).where(*conditions)
        total = self.session.exec(count_stmt).one()

        # Fetch paginated results
        query = (
            select(Usuario)
            .where(*conditions)
            .offset(skip)
            .limit(limit)
        )
        items = list(self.session.exec(query))

        return items, total

    def soft_delete(self, id: int) -> Usuario | None:
        """Soft-delete a user by setting eliminado_en.

        Args:
            id: User ID to soft-delete.

        Returns:
            Updated Usuario instance, or None if not found.
        """
        user = self.get(id)
        if user is None:
            return None

        user.eliminado_en = datetime.now(timezone.utc)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
