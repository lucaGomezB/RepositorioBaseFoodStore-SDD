# RefreshToken Repository
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.core.repositories.base import BaseRepository
from app.models.refresh_token import RefreshToken


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository for RefreshToken model."""

    def __init__(self, session: Session):
        super().__init__(RefreshToken, session)

    def create_token(self, token: str, user_id: int, expires_at: str) -> RefreshToken:
        """Create a new refresh token."""
        now = datetime.now(timezone.utc).isoformat()
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            created_at=now,
            revoked=False
        )
        return self.create(refresh_token)

    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string."""
        return self.get_by_field("token", token)

    def get_valid_token(self, token: str) -> Optional[RefreshToken]:
        """Get a valid (non-revoked, non-expired) refresh token."""
        statement = select(RefreshToken).where(
            RefreshToken.token == token,
            not RefreshToken.revoked
        )
        result = self.session.exec(statement).first()

        if result:
            # Check expiration - handle both timezone-aware and naive datetimes
            exp_str = result.expires_at.replace("Z", "+00:00")
            exp = datetime.fromisoformat(exp_str)
            # Make sure exp is timezone-aware
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if now > exp:
                return None

        return result

    def revoke_token(self, token: str) -> bool:
        """Revoke a refresh token."""
        refresh_token = self.get_by_token(token)
        if refresh_token:
            refresh_token.revoked = True
            refresh_token.revoked_at = datetime.now(timezone.utc).isoformat()
            self.session.add(refresh_token)
            self.session.commit()
            return True
        return False

    def revoke_all_user_tokens(self, user_id: int) -> bool:
        """Revoke all refresh tokens for a user."""
        statement = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            not RefreshToken.revoked
        )
        tokens = list(self.session.exec(statement))

        now = datetime.now(timezone.utc).isoformat()
        for token in tokens:
            token.revoked = True
            token.revoked_at = now
            self.session.add(token)

        if tokens:
            self.session.commit()
            return True
        return False
