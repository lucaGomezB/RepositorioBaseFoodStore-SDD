# RefreshToken model for storing refresh tokens
from sqlmodel import Field, SQLModel
from typing import Optional


class RefreshToken(SQLModel, table=True):
    """Store refresh tokens for session management."""
    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(max_length=500, unique=True, index=True)
    user_id: int = Field(foreign_key="usuarios.id")
    expires_at: str = Field(max_length=50)  # ISO timestamp
    created_at: str = Field(max_length=50, default=None)
    revoked: bool = Field(default=False)
    revoked_at: Optional[str] = Field(default=None, max_length=50)