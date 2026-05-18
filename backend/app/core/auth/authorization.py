# Authorization dependencies for RBAC
from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_db
from app.core.auth.deps import get_current_user, TokenPayload
from app.core.auth.roles import Role


def require_roles(*allowed_roles: Role):
    """
    Dependency factory that verifies the current user has one of the allowed roles.
    
    Also checks that the user exists in the database and is active (not soft-deleted).
    
    Returns a callable compatible with FastAPI `Depends()`. Usage:
    
        @router.get("/admin-only")
        def admin_endpoint(
            current_user: TokenPayload = Depends(require_roles(Role.ADMIN))
        ):
            ...
    
    Can also be used as a sub-dependency inside other dependency functions,
    wrapped explicitly in Depends():
    
        def require_admin(
            current_user: TokenPayload = Depends(require_roles(Role.ADMIN))
        ) -> TokenPayload:
            return current_user
    
    Args:
        *allowed_roles: One or more Role values that are permitted access.
        
    Returns:
        A callable that FastAPI can resolve as a dependency. Returns
        TokenPayload on success or raises HTTPException on failure.
        
    Raises:
        HTTPException: 401 if no valid token (from get_current_user)
        HTTPException: 403 if user is inactive/deleted or role insufficient
    """
    allowed_ids = {role.value for role in allowed_roles}

    def _check_role(
        current_user: TokenPayload = Depends(get_current_user),
        session: Session = Depends(get_db),
    ) -> TokenPayload:
        # Verify user exists in DB and is active (not soft-deleted)
        from app.models.usuario import Usuario
        from app.core.repositories.base import BaseRepository
        user_repo = BaseRepository(Usuario, session)
        db_user = user_repo.get(current_user.user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if not db_user.activo or db_user.eliminado_en is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive or deleted",
            )

        # Check if ANY of the user's roles intersect with allowed roles
        user_role_ids = set(current_user.roles)
        if not user_role_ids.intersection(allowed_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check_role
