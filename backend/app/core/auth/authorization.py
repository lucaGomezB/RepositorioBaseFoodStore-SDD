# Authorization dependencies for RBAC
from fastapi import Depends, HTTPException, status

from app.core.auth.deps import get_current_user, TokenPayload
from app.core.auth.roles import Role


def require_roles(*allowed_roles: Role):
    """
    Dependency factory that verifies the current user has one of the allowed roles.
    
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
        HTTPException: 403 if user's role is not in allowed_roles
    """
    allowed_ids = {role.value for role in allowed_roles}

    def _check_role(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if current_user.rol_id not in allowed_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check_role
