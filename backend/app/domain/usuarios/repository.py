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
        from app.models.usuario_rol import UsuarioRol
        statement = (
            select(Usuario)
            .join(UsuarioRol, Usuario.id == UsuarioRol.usuario_id)
            .where(
                UsuarioRol.rol_id == rol_id,
                Usuario.eliminado_en.is_(None),
            )
        )
        return list(self.session.exec(statement).unique())

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
        from app.models.usuario_rol import UsuarioRol

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
            # Users that have this role (via UsuarioRol)
            subq = select(UsuarioRol.usuario_id).where(UsuarioRol.rol_id == rol_id).scalar_subquery()
            conditions.append(Usuario.id.in_(subq))

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
        items = list(self.session.exec(query).unique())

        return items, total

    def add_role(self, usuario_id: int, rol_id: int) -> None:
        """Add a role to a user."""
        from app.models.usuario_rol import UsuarioRol
        existing = self.session.exec(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_id == rol_id,
            )
        ).first()
        if not existing:
            self.session.add(UsuarioRol(usuario_id=usuario_id, rol_id=rol_id))

    def remove_role(self, usuario_id: int, rol_id: int) -> bool:
        """Remove a role from a user. Returns True if removed, False if not found."""
        from app.models.usuario_rol import UsuarioRol
        existing = self.session.exec(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == usuario_id,
                UsuarioRol.rol_id == rol_id,
            )
        ).first()
        if existing:
            self.session.delete(existing)
            return True
        return False

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
        user.activo = False
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def restore(self, id: int) -> Usuario | None:
        """Restore a soft-deleted user by clearing eliminado_en and reactivating.

        Args:
            id: User ID to restore.

        Returns:
            Updated Usuario instance, or None if not found.
        """
        user = self.get(id)
        if user is None:
            return None

        user.eliminado_en = None
        user.activo = True
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
