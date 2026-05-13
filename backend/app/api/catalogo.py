# Public Catalog Router
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.auth.deps import TokenPayload, get_current_user_optional
from app.core.schemas.producto import (
    ProductoCatalogoRead,
    CatalogoResponse,
)
from app.core.services.producto import ProductoService

router = APIRouter(prefix="/catalogo/productos", tags=["Catálogo Público"])


@router.get("/", response_model=CatalogoResponse)
def get_catalogo_productos(
    page: int = 1,
    limit: int = 20,
    categoria_id: Optional[int] = None,
    busqueda: Optional[str] = None,
    disponible: Optional[bool] = None,
    excluir_alergenos: Optional[str] = None,
    session: Session = Depends(get_db),
    current_user: Optional[TokenPayload] = Depends(get_current_user_optional),
):
    """Get public catalog products. No auth required.

    For unauthenticated users, defaults to disponible=true (public catalog).
    Authenticated users can override the default or see non-available products.
    Supports pagination via page/limit and allergen exclusion filter.
    """
    # For anonymous users, default to only available products (RN-CA08)
    if disponible is None and not current_user:
        disponible = True

    productos, total_count = ProductoService.get_catalogo(
        session,
        page=page,
        limit=limit,
        categoria_id=categoria_id,
        busqueda=busqueda,
        disponible=disponible,
        excluir_alergenos=excluir_alergenos,
    )
    return CatalogoResponse(items=productos, total_count=total_count)


@router.get("/{producto_id}", response_model=ProductoCatalogoRead)
def get_catalogo_producto_detalle(
    producto_id: int,
    session: Session = Depends(get_db),
):
    """Get public product detail with ingredients, categories, and hay_stock.

    Returns 404 if product not found, soft-deleted, or not available.
    """
    producto = ProductoService.get_detalle_publico(session, producto_id)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return producto
