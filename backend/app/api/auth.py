# Auth endpoints
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.auth.tokens import create_access_token, create_refresh_token, decode_token, verify_token_type
from app.core.auth.deps import get_current_user, TokenPayload
from app.core.repositories import UsuarioRepository, RefreshTokenRepository
from app.core.config import settings
from app.core.middleware.rate_limiter import limiter


router = APIRouter(prefix="/auth", tags=["Auth"])


# --- Schemas ---

class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    nombre: str
    apellido: str
    rol_id: int
    activo: bool
    
    class Config:
        from_attributes = True


# --- Endpoints ---

@router.post("/login", response_model=TokenResponse)
@limiter.limit(f"{settings.RATE_LIMIT_LOGIN_REQUESTS}/minute")
def login(
    request: Request,
    data: LoginRequest,
    session: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.
    
    Args:
        data: Login credentials (email, password)
        session: Database session
        
    Returns:
        access_token and refresh_token
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by email
    usuario_repo = UsuarioRepository(session)
    user = usuario_repo.get_by_email(data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password using bcrypt
    import bcrypt
    if not bcrypt.checkpw(data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "rol_id": user.rol_id
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Store refresh token in database
    refresh_token_repo = RefreshTokenRepository(session)
    expires_at = (datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
    refresh_token_repo.create_token(refresh_token, user.id, expires_at)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    data: RefreshRequest,
    session: Session = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.
    
    Args:
        data: Refresh token
        session: Database session
        
    Returns:
        New access_token and refresh_token
        
    Raises:
        HTTPException: 401 if refresh token is invalid or expired
    """
    # Verify token type
    if not verify_token_type(data.refresh_token, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Decode to get user info
    payload = decode_token(data.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Check if refresh token exists in database and is valid
    refresh_token_repo = RefreshTokenRepository(session)
    stored_token = refresh_token_repo.get_valid_token(data.refresh_token)
    
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or revoked"
        )
    
    # Get user
    user_id = payload.get("user_id")
    usuario_repo = UsuarioRepository(session)
    user = usuario_repo.get(user_id)
    
    if not user or not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "rol_id": user.rol_id
    }
    
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    # Revoke old refresh token and create new one
    refresh_token_repo.revoke_token(data.refresh_token)
    expires_at = (datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
    refresh_token_repo.create_token(new_refresh_token, user.id, expires_at)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
def logout(
    data: RefreshRequest,
    current_user: TokenPayload = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Logout user by revoking the refresh token.
    
    Args:
        data: Refresh token to revoke
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        Success message
    """
    # Revoke the refresh token
    refresh_token_repo = RefreshTokenRepository(session)
    refresh_token_repo.revoke_token(data.refresh_token)
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: TokenPayload = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        User information
    """
    usuario_repo = UsuarioRepository(session)
    user = usuario_repo.get(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user