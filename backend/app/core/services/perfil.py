# Perfil Service
from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.usuario import Usuario
from app.core.repositories.base import BaseRepository
from app.core.repositories.refresh_token import RefreshTokenRepository


class PerfilService:
    """Service for user profile operations."""

    @staticmethod
    def get_profile(session: Session, usuario_id: int) -> Usuario:
        """Get user profile by user ID.

        Args:
            session: Database session
            usuario_id: User ID to look up

        Returns:
            Usuario instance

        Raises:
            HTTPException: 404 if user not found
        """
        repo = BaseRepository(Usuario, session)
        user = repo.get(usuario_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        return user

    @staticmethod
    def update_profile(session: Session, usuario_id: int, data: dict) -> Usuario:
        """Update user profile.

        Only nombre and telefono can be updated. Email is never changed.

        Args:
            session: Database session
            usuario_id: User ID
            data: Dictionary with fields to update (nombre, telefono)

        Returns:
            Updated Usuario instance

        Raises:
            HTTPException: 404 if user not found
        """
        repo = BaseRepository(Usuario, session)
        user = repo.get(usuario_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        # Only allow updating specific fields; never email
        allowed_fields = {"nombre", "telefono"}
        values = {k: v for k, v in data.items() if k in allowed_fields and v is not None}

        for key, value in values.items():
            if hasattr(user, key):
                setattr(user, key, value)

        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @staticmethod
    def change_password(
        session: Session,
        usuario_id: int,
        password_actual: str,
        password_nueva: str,
    ) -> None:
        """Change user password.

        Verifies the current password, hashes the new one, persists it,
        and revokes all existing refresh tokens for the user.

        Args:
            session: Database session
            usuario_id: User ID
            password_actual: Current password for verification
            password_nueva: New password to set

        Raises:
            HTTPException: 400 if current password is incorrect
            HTTPException: 404 if user not found
        """
        import bcrypt
        from datetime import datetime, timezone

        repo = BaseRepository(Usuario, session)
        user = repo.get(usuario_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        # Verify current password
        if not bcrypt.checkpw(
            password_actual.encode("utf-8"),
            user.password_hash.encode("utf-8"),
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta",
            )

        # Hash new password with cost factor >= 12
        new_hash = bcrypt.hashpw(
            password_nueva.encode("utf-8"),
            bcrypt.gensalt(12),
        ).decode("utf-8")

        user.password_hash = new_hash
        user.fecha_actualizacion = datetime.now(timezone.utc).isoformat()
        session.add(user)
        session.commit()

        # Revoke all existing refresh tokens for this user
        refresh_token_repo = RefreshTokenRepository(session)
        refresh_token_repo.revoke_all_user_tokens(usuario_id)
