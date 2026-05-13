# Categorias Router
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List

from app.core.database import get_db
from app.core.auth.roles import Role
from app.core.auth.authorization import require_roles
from app.schemas.categoria import (
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaResponse,
    CategoriaTree,
)
from app.services.categoria import CategoriaService

router = APIRouter(prefix="/categorias", tags=["Categorias"])


# --- Public Endpoints (no auth required) ---

@router.get("/", response_model=List[CategoriaTree])
def read_categorias_tree(
    incluir_eliminados: bool = Query(default=False, alias="incluir_eliminados"),
    session: Session = Depends(get_db),
):
    """
    Get all categories as a hierarchical tree.
    Public - no authentication required.
    """
    service = CategoriaService(session)
    return service.get_tree(include_deleted=incluir_eliminados)


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def read_categoria(categoria_id: int, session: Session = Depends(get_db)):
    """
    Get a single category by ID.
    Public - no authentication required.
    """
    service = CategoriaService(session)
    return service.get_by_id(categoria_id)


# --- Protected Endpoints (STOCK, ADMIN) ---

@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def create_categoria(
    data: CategoriaCreate,
    session: Session = Depends(get_db),
    current_user=Depends(require_roles(Role.STOCK, Role.ADMIN)),
):
    """Create a new category. Requires STOCK or ADMIN role."""
    service = CategoriaService(session)
    return service.create(data)


@router.put("/{categoria_id}", response_model=CategoriaResponse)
def update_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    session: Session = Depends(get_db),
    current_user=Depends(require_roles(Role.STOCK, Role.ADMIN)),
):
    """Update a category. Requires STOCK or ADMIN role."""
    service = CategoriaService(session)
    return service.update(categoria_id, data)


@router.delete("/{categoria_id}", response_model=CategoriaResponse)
def delete_categoria(
    categoria_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(require_roles(Role.STOCK, Role.ADMIN)),
):
    """Soft delete a category. Requires STOCK or ADMIN role."""
    service = CategoriaService(session)
    return service.soft_delete(categoria_id)
