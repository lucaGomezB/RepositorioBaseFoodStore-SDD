# Auth dependencies for FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.auth.tokens import decode_token, verify_token_type
from app.core.auth.roles import Role
from app.models.usuario import Usuario
from app.core.repositories import UsuarioRepository

# Security scheme
security = HTTPBearer()


class TokenPayload:
    """Token payload data class."""
    def __init__(self, user_id: int, email: str, rol_id: int):
        self.user_id = user_id
        self.email = email
        self.rol_id = rol_id


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_db)
) -> TokenPayload:
    """
    Extract and validate the current user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        session: Database session
        
    Returns:
        TokenPayload with user information
        
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    token = credentials.credentials
    
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
    rol_id = payload.get("rol_id")
    
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenPayload(user_id=user_id, email=email, rol_id=rol_id)


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
    if current_user.rol_id != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    session: Session = Depends(get_db)
) -> Optional[TokenPayload]:
    """
    Optional current user - returns None if no valid token.
    Use this for endpoints that work with or without auth.
    
    Args:
        credentials: Optional HTTP Authorization credentials
        session: Database session
        
    Returns:
        TokenPayload if valid token, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, session)
    except HTTPException:
        return None