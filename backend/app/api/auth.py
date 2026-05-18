# Auth endpoints
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional

from app.core.database import get_db
from app.core.uow import UnitOfWork
from app.core.auth.tokens import create_access_token, create_refresh_token, decode_token, verify_token_type
from app.core.auth.deps import get_current_user, TokenPayload
from app.core.auth.roles import Role
from app.core.auth.authorization import require_roles
from app.domain.usuarios.repository import UsuarioRepository
from app.domain.auth.repository import RefreshTokenRepository
from app.core.config import settings
from app.models.usuario import Usuario
from app.core.middleware.rate_limiter import limiter


router = APIRouter(prefix="/auth", tags=["Auth"])


# --- Schemas ---

class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@foodstore.com",
                "password": "admin123",
            },
        },
    }


class TokenResponse(BaseModel):
    """Token response schema (legacy — kept for backward compat)."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
            },
        },
    }


class RefreshRequest(BaseModel):
    """Refresh token request schema (legacy body fallback).
    
    The refresh_token is optional here because modern clients send it
    via httpOnly cookie. The body fallback exists for API clients/tests
    that send the token directly.
    """
    refresh_token: Optional[str] = None
    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            },
        },
    }


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    nombre: str
    apellido: str
    roles: list[int] = []
    activo: bool
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "admin@foodstore.com",
                "nombre": "Admin",
                "apellido": "User",
                "roles": [1],
                "activo": True,
            },
        },
    )


class AssignRoleRequest(BaseModel):
    """Schema for assigning a role to a user."""
    rol_id: int
    action: str = "add"  # "add" or "remove"
    model_config = {
        "json_schema_extra": {
            "example": {
                "rol_id": 2,
                "action": "add",
            },
        },
    }


class RegisterRequest(BaseModel):
    """Register request schema."""
    email: EmailStr
    password: str
    nombre: str
    apellido: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "cliente@foodstore.com",
                "password": "MiPassword123!",
                "nombre": "Juan",
                "apellido": "Perez",
            },
        },
    }


class LogoutResponse(BaseModel):
    """Logout response schema."""
    message: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Logged out successfully",
            },
        },
    }


# --- Helper ---

def _build_auth_response(
    access_token: str,
    refresh_token: str,
    user,
    status_code: int = 200,
) -> JSONResponse:
    """
    Build a JSONResponse with user data and httpOnly cookies.
    Used by login() and refresh_token() to keep the cookie logic in one place.
    """
    max_age_access = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    max_age_refresh = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    response = JSONResponse(
        status_code=status_code,
        content={
            "token_type": "bearer",
            "expires_in": max_age_access,
            "user": {
                "id": user.id,
                "email": user.email,
                "nombre": user.nombre,
                "apellido": user.apellido,
                "roles": user.rol_ids,
                "activo": user.activo,
            },
        },
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=max_age_access,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=max_age_refresh,
        path="/",
    )

    return response


def _extract_refresh_token(request: Request, data: Optional[RefreshRequest] = None) -> str:
    """
    Extract refresh token from cookie first, fall back to request body.
    
    Priority:
    1. refresh_token cookie (httpOnly — preferred for browser clients)
    2. refresh_token field in request body (legacy — for API clients / tests)
    """
    # Try cookie first
    token_from_cookie = request.cookies.get("refresh_token")
    if token_from_cookie:
        return token_from_cookie

    # Fall back to body
    if data and data.refresh_token:
        return data.refresh_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No refresh token provided",
    )


# --- Endpoints ---

@router.post("/login")
@limiter.limit(f"{settings.RATE_LIMIT_LOGIN_REQUESTS}/minute")
def login(
    request: Request,
    data: LoginRequest,
    session: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens via httpOnly cookies.
    
    Sets access_token and refresh_token as httpOnly, sameSite=Lax cookies.
    Returns user info in the JSON body (tokens are NOT exposed to JS).
    
    Args:
        data: Login credentials (email, password)
        session: Database session
        
    Returns:
        JSONResponse with user data and httpOnly cookies
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    with UnitOfWork(session) as uow:
        # Find user by email
        usuario_repo = UsuarioRepository(uow.session)
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
        "roles": user.rol_ids,
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Store refresh token in database
    with UnitOfWork(session) as uow:
        refresh_token_repo = RefreshTokenRepository(uow.session)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
        refresh_token_repo.create_token(refresh_token, user.id, expires_at)
    
    return _build_auth_response(access_token, refresh_token, user)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: RegisterRequest,
    session: Session = Depends(get_db),
):
    """Register a new user with CLIENT role (RN-AU07).
    
    The role is auto-assigned in the service layer, NOT taken from the request.
    """
    from app.core.security import hash_password
    from app.models.usuario_rol import UsuarioRol
    
    # Check if email already exists
    existing = session.query(Usuario).filter(Usuario.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    now = datetime.now(timezone.utc).isoformat()
    user = Usuario(
        email=data.email,
        password_hash=hash_password(data.password),
        nombre=data.nombre,
        apellido=data.apellido,
        activo=True,
        fecha_creacion=now,
        fecha_actualizacion=now,
    )
    session.add(user)
    session.flush()  # Get user.id
    
    # Auto-assign CLIENT role (RN-AU07)
    user_rol = UsuarioRol(usuario_id=user.id, rol_id=Role.CLIENT.value)
    session.add(user_rol)
    session.commit()
    session.refresh(user)
    
    return {
        "id": user.id,
        "email": user.email,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "roles": user.rol_ids,
        "activo": user.activo,
    }


@router.post("/refresh")
def refresh_token(
    request: Request,
    data: Optional[RefreshRequest] = None,
    session: Session = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token from httpOnly cookie.
    
    Reads the refresh_token from the httpOnly cookie. Falls back to the
    request body for legacy API clients / tests.
    
    Returns:
        JSONResponse with new httpOnly cookies (token rotation)
        
    Raises:
        HTTPException: 401 if refresh token is invalid or expired
    """
    # Extract refresh token from cookie or body
    refresh_token_value = _extract_refresh_token(request, data)
    
    # Verify token type
    if not verify_token_type(refresh_token_value, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Decode to get user info
    payload = decode_token(refresh_token_value)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    with UnitOfWork(session) as uow:
        # Check if refresh token exists in database and is valid
        refresh_token_repo = RefreshTokenRepository(uow.session)
        stored_token = refresh_token_repo.get_valid_token(refresh_token_value)
        
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or revoked"
            )
        
        # Get user
        user_id = payload.get("user_id")
        usuario_repo = UsuarioRepository(uow.session)
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
            "roles": user.rol_ids,
        }
        
        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        # Revoke old refresh token and create new one
        refresh_token_repo.revoke_token(refresh_token_value)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
        refresh_token_repo.create_token(new_refresh_token, user.id, expires_at)
    
    return _build_auth_response(access_token, new_refresh_token, user)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    request: Request,
    data: Optional[RefreshRequest] = None,
    current_user: TokenPayload = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """
    Logout user by revoking the refresh token and clearing cookies.
    
    Reads the refresh_token from httpOnly cookie (falls back to body).
    Revokes the token and clears both auth cookies.
    
    Args:
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        Success message
    """
    refresh_token_value = _extract_refresh_token(request, data)
    
    with UnitOfWork(session) as uow:
        refresh_token_repo = RefreshTokenRepository(uow.session)
        refresh_token_repo.revoke_token(refresh_token_value)
    
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return response


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
    with UnitOfWork(session) as uow:
        usuario_repo = UsuarioRepository(uow.session)
        user = usuario_repo.get(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "roles": user.rol_ids,
        "activo": user.activo,
    }


@router.put("/users/{user_id}/role", response_model=UserResponse)
def assign_user_role(
    user_id: int,
    data: AssignRoleRequest,
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
    session: Session = Depends(get_db),
):
    """
    Assign or remove a role from a user. Admin only.
    
    RN-RB04: If removing ADMIN role from self, prevent if last admin.
    
    Args:
        user_id: Target user ID
        data: Role assignment (rol_id + action)
        current_user: Authenticated admin user
        session: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: 404 if user not found
        HTTPException: 400 if last admin tries to self-remove admin (RN-RB04)
        HTTPException: 403 if caller is not admin
    """
    with UnitOfWork(session) as uow:
        usuario_repo = UsuarioRepository(uow.session)
        user = usuario_repo.get(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # If removing ADMIN role from self, check RN-RB04
        if data.action == "remove" and data.rol_id == Role.ADMIN.value and user_id == current_user.user_id:
            admin_users = usuario_repo.get_by_rol(Role.ADMIN.value)
            if len(admin_users) <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove admin role from the last administrator",
                )

        # Execute the action
        if data.action == "add":
            usuario_repo.add_role(user_id, data.rol_id)
        elif data.action == "remove":
            usuario_repo.remove_role(user_id, data.rol_id)

        uow.session.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "roles": user.rol_ids,
        "activo": user.activo,
    }