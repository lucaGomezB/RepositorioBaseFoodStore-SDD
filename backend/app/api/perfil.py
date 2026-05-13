# Perfil Router
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_db
from app.core.auth.deps import TokenPayload
from app.core.auth.authorization import require_roles
from app.core.auth.roles import Role
from app.core.schemas.perfil import PerfilResponse, PerfilUpdate, PasswordChange
from app.core.services.perfil import PerfilService

router = APIRouter(prefix="/perfil", tags=["Perfil"])


@router.get("/", response_model=PerfilResponse)
def get_perfil(
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """Get current authenticated user's profile.

    Returns nombre, email, telefono, fecha_creacion.
    """
    return PerfilService.get_profile(session, current_user.user_id)


@router.put("/", response_model=PerfilResponse)
def update_perfil(
    data: PerfilUpdate,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """Update current user's profile (nombre, telefono). Email cannot be changed."""
    return PerfilService.update_profile(
        session, current_user.user_id, data.model_dump(exclude_unset=True)
    )


@router.put("/password")
def change_password(
    data: PasswordChange,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """Change current user's password.

    Verifies current password, hashes and persists new one,
    and revokes all existing refresh tokens.
    """
    PerfilService.change_password(
        session,
        current_user.user_id,
        data.password_actual,
        data.password_nueva,
    )
    return {"detail": "Contraseña actualizada correctamente"}
