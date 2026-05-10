# Security helpers: password hashing and JWT configuration
import bcrypt
from typing import Optional
from app.core.config import settings


# ====================
# Password Hashing
# ====================


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password as string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hashed password

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


# ====================
# JWT Configuration
# ====================


class JWTConfig:
    """JWT configuration constants."""

    SECRET_KEY: str = settings.SECRET_KEY
    ALGORITHM: str = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS: int = settings.REFRESH_TOKEN_EXPIRE_DAYS


# For convenience, also expose as a singleton
jwt_config = JWTConfig()