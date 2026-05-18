# Ingredientes Router
from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import List

from app.core.database import get_db
from app.core.uow import UnitOfWork
from app.core.auth.roles import Role
from app.core.auth.authorization import require_roles
from app.domain.ingredientes.schemas import (
    IngredienteCreate,
    IngredienteUpdate,
    IngredienteResponse,
)
from app.domain.ingredientes.service import IngredienteService

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])


# --- Public Endpoints (no auth required) ---

@router.get("/", response_model=List[IngredienteResponse])
def read_ingredientes(
    es_alergeno: bool = Query(default=None),
    session: Session = Depends(get_db),
):
    """
    Get all ingredients. Optional filter by es_alergeno.
    Public - no authentication required.
    """
    with UnitOfWork(session) as uow:
        service = IngredienteService(uow)
        return service.get_all(es_alergeno=es_alergeno)


@router.get("/{ingrediente_id}", response_model=IngredienteResponse)
def read_ingrediente(ingrediente_id: int, session: Session = Depends(get_db)):
    """
    Get a single ingredient by ID.
    Public - no authentication required.
    """
    with UnitOfWork(session) as uow:
        service = IngredienteService(uow)
        return service.get_by_id(ingrediente_id)


# --- Protected Endpoints (STOCK, ADMIN) ---

@router.post("/", response_model=IngredienteResponse, status_code=status.HTTP_201_CREATED)
def create_ingrediente(
    data: IngredienteCreate,
    session: Session = Depends(get_db),
    current_user=Depends(require_roles(Role.STOCK, Role.ADMIN)),
):
    """Create a new ingredient. Requires STOCK or ADMIN role."""
    with UnitOfWork(session) as uow:
        service = IngredienteService(uow)
        return service.create(data)


@router.put("/{ingrediente_id}", response_model=IngredienteResponse)
def update_ingrediente(
    ingrediente_id: int,
    data: IngredienteUpdate,
    session: Session = Depends(get_db),
    current_user=Depends(require_roles(Role.STOCK, Role.ADMIN)),
):
    """Update an ingredient. Requires STOCK or ADMIN role."""
    with UnitOfWork(session) as uow:
        service = IngredienteService(uow)
        return service.update(ingrediente_id, data)


@router.delete("/{ingrediente_id}", response_model=IngredienteResponse)
def delete_ingrediente(
    ingrediente_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(require_roles(Role.STOCK, Role.ADMIN)),
):
    """Soft delete an ingredient. Requires STOCK or ADMIN role."""
    with UnitOfWork(session) as uow:
        service = IngredienteService(uow)
        return service.soft_delete(ingrediente_id)
