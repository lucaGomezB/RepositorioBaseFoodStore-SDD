# Direcciones Router
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.core.database import get_db
from app.core.auth.deps import TokenPayload
from app.core.auth.authorization import require_roles
from app.core.auth.roles import Role
from app.core.schemas.direccion import (
    DireccionCreate,
    DireccionUpdate,
    DireccionResponse,
)
from app.core.services.direccion import DireccionService

router = APIRouter(prefix="/direcciones", tags=["Direcciones"])


@router.post("/", response_model=DireccionResponse, status_code=status.HTTP_201_CREATED)
def crear_direccion(
    data: DireccionCreate,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """Create a new delivery address for the current user.
    
    If this is the user's first address, it is auto-marked as default (RN-DI01).
    """
    return DireccionService.crear(session, current_user.user_id, data.model_dump())


@router.get("/", response_model=List[DireccionResponse])
def listar_direcciones(
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """List all addresses for the current user."""
    return DireccionService.listar_por_usuario(session, current_user.user_id)


@router.put("/{direccion_id}", response_model=DireccionResponse)
def actualizar_direccion(
    direccion_id: int,
    data: DireccionUpdate,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """Update a delivery address. Validates ownership - returns 404 if not found or not owned."""
    direccion = DireccionService.actualizar(
        session, direccion_id, current_user.user_id, data.model_dump(exclude_unset=True)
    )
    if not direccion:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    return direccion


@router.delete("/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_direccion(
    direccion_id: int,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """Delete a delivery address. Validates ownership - returns 404 if not found or not owned."""
    if not DireccionService.eliminar(session, direccion_id, current_user.user_id):
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    return None


@router.patch("/{direccion_id}/predeterminada", response_model=DireccionResponse)
def marcar_predeterminada(
    direccion_id: int,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.CLIENT, Role.ADMIN)),
):
    """Set an address as default. Atomically unsets the previous default (RN-DI02).
    Returns 404 if address not found or not owned.
    """
    direccion = DireccionService.marcar_predeterminada(
        session, direccion_id, current_user.user_id
    )
    if not direccion:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    return direccion
