# Auth dependencies for FastAPI
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.auth.tokens import decode_token, verify_token_type
from app.core.auth.roles import Role
from app.models.usuario import Usuario

# Security scheme — auto_error=False so we can fall back to cookies
security = HTTPBearer(auto_error=False)


class TokenPayload:
    """Token payload data class."""
    def __init__(self, user_id: int, email: str, roles: list[int]):
        self.user_id = user_id
        self.email = email
        self.roles = roles

    @property
    def rol_id(self) -> int:
        """Primary role (first role). For backward compatibility."""
        return self.roles[0] if self.roles else 4


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None),
    session: Session = Depends(get_db)
) -> TokenPayload:
    """
    Extract and validate the current user from JWT token.
    
    Supports two token sources (in priority order):
    1. Authorization: Bearer <token> header (API clients, tests)
    2. access_token httpOnly cookie (browser clients)
    
    Args:
        credentials: Optional HTTP Authorization credentials (Bearer token)
        access_token: Optional token from httpOnly cookie
        session: Database session
        
    Returns:
        TokenPayload with user information
        
    Raises:
        HTTPException: 401 if no token is provided or token is invalid
    """
    # Try Authorization header first, then cookie
    token = None
    if credentials is not None:
        token = credentials.credentials
    elif access_token is not None:
        token = access_token
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify it's an access token
    if not verify_token_type(token, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user info from payload
    user_id = payload.get("user_id")
    email = payload.get("email")
    roles = payload.get("roles", [])
    
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenPayload(user_id=user_id, email=email, roles=roles)


def get_current_active_user(
    current_user: TokenPayload = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Usuario:
    """
    Get current user and verify they are active.
    
    Args:
        current_user: Current user from token
        session: Database session
        
    Returns:
        Usuario model instance
        
    Raises:
        HTTPException: 403 if user is inactive
    """
    from app.core.repositories import BaseRepository
    
    user_repo = BaseRepository(Usuario, session)
    user = user_repo.get(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


def require_admin(
    current_user: TokenPayload = Depends(get_current_user)
) -> TokenPayload:
    """
    Verify that the current user has admin role.
    
    Convenience wrapper for backward compatibility. Checks that the
    current user's role is ADMIN (role_id == 1).
    
    Args:
        current_user: Current user from token
        
    Returns:
        TokenPayload if user is admin
        
    Raises:
        HTTPException: 403 if user is not admin
    """
    if Role.ADMIN.value not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    access_token: Optional[str] = Cookie(None),
    session: Session = Depends(get_db)
) -> Optional[TokenPayload]:
    """
    Optional current user - returns None if no valid token.
    Use this for endpoints that work with or without auth.
    
    Supports both Authorization header and httpOnly cookie.
    
    Args:
        credentials: Optional HTTP Authorization credentials
        access_token: Optional token from httpOnly cookie
        session: Database session
        
    Returns:
        TokenPayload if valid token, None otherwise
    """
    try:
        return get_current_user(credentials, access_token, session)
    except HTTPException:
        return None