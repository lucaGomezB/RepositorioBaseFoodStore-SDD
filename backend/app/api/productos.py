# Producto Router
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.auth.deps import TokenPayload, get_current_user_optional
from app.core.auth.authorization import require_roles
from app.core.auth.roles import Role
from app.core.schemas.producto import (
    ProductoRead,
    ProductoCreate,
    ProductoUpdate,
    ProductoIngredienteRead,
    ProductoCategoriaRead,
    IngredienteAsignado,
    CategoriaAsignada,
    StockUpdate,
)
from app.core.services.producto import ProductoService

router = APIRouter(prefix="/productos", tags=["Productos"])


# --- Public Endpoints (GET) ---

@router.get("/", response_model=List[ProductoRead])
def read_productos(
    skip: int = 0,
    limit: int = 100,
    categoria_id: Optional[int] = None,
    busqueda: Optional[str] = None,
    disponible: Optional[bool] = None,
    incluir_eliminados: bool = False,
    session: Session = Depends(get_db),
    current_user: Optional[TokenPayload] = Depends(get_current_user_optional),
):
    """Get all products. Public - no auth required.

    The `incluir_eliminados` parameter requires ADMIN or STOCK role.
    Regular users and unauthenticated requests will have it silently ignored.
    """
    if incluir_eliminados and (not current_user or current_user.rol_id not in (Role.ADMIN, Role.STOCK)):
        incluir_eliminados = False
    return ProductoService.get_all(
        session,
        skip=skip,
        limit=limit,
        categoria_id=categoria_id,
        busqueda=busqueda,
        disponible=disponible,
        incluir_eliminados=incluir_eliminados,
    )


@router.get("/{producto_id}", response_model=ProductoRead)
def read_producto(producto_id: int, session: Session = Depends(get_db)):
    """Get a product by ID. Public - no auth required."""
    producto = ProductoService.get_by_id(session, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


# --- Protected Endpoints (require ADMIN or STOCK) ---

@router.post("/", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def create_producto(
    data: ProductoCreate,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK)),
):
    """Create a new product. Admin or Stock only."""
    producto_data = data.model_dump()
    return ProductoService.create(session, producto_data)


@router.patch("/{producto_id}", response_model=ProductoRead)
def update_producto(
    producto_id: int,
    data: ProductoUpdate,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK)),
):
    """Update a product. Admin or Stock only."""
    producto_data = data.model_dump(exclude_unset=True)
    producto = ProductoService.update(session, producto_id, producto_data)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(
    producto_id: int,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK)),
):
    """Delete a product (soft delete). Admin or Stock only."""
    if not ProductoService.delete(session, producto_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return None


# --- Stock endpoint ---

@router.patch("/{producto_id}/stock", response_model=ProductoRead)
def update_producto_stock(
    producto_id: int,
    data: StockUpdate,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK)),
):
    """Atomically update product stock. Admin or Stock only."""
    return ProductoService.actualizar_stock(session, producto_id, data.cantidad)


# --- Relationships Producto-Ingrediente ---

@router.get("/{producto_id}/ingredientes", response_model=List[ProductoIngredienteRead])
def get_producto_ingredientes(producto_id: int, session: Session = Depends(get_db)):
    """Get ingredients for a product. Public - no auth required."""
    return ProductoService.get_ingredientes(session, producto_id)


@router.post("/{producto_id}/ingredientes", response_model=List[ProductoIngredienteRead])
def add_producto_ingrediente(
    producto_id: int,
    data: IngredienteAsignado,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK))
):
    """Add an ingredient to a product. Admin or Stock only."""
    result = ProductoService.add_ingrediente(session, producto_id, data.model_dump())
    if result is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result


@router.put("/{producto_id}/ingredientes", response_model=List[ProductoIngredienteRead])
def replace_producto_ingredientes(
    producto_id: int,
    data: List[IngredienteAsignado],
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK))
):
    """Replace all ingredients for a product atomically. Admin or Stock only."""
    result = ProductoService.reemplazar_ingredientes(
        session, producto_id, [ing.model_dump() for ing in data]
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result


@router.delete("/{producto_id}/ingredientes/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_producto_ingrediente(
    producto_id: int,
    ingrediente_id: int,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK))
):
    """Remove an ingredient from a product. Admin or Stock only."""
    if not ProductoService.remove_ingrediente(session, producto_id, ingrediente_id):
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    return None


# --- Relationships Producto-Categoría ---

@router.get("/{producto_id}/categorias", response_model=List[ProductoCategoriaRead])
def get_producto_categorias(producto_id: int, session: Session = Depends(get_db)):
    """Get categories for a product. Public - no auth required."""
    return ProductoService.get_categorias(session, producto_id)


@router.post("/{producto_id}/categorias", response_model=List[ProductoCategoriaRead])
def add_producto_categoria(
    producto_id: int,
    data: CategoriaAsignada,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK))
):
    """Add a category to a product. Admin or Stock only."""
    result = ProductoService.add_categoria(session, producto_id, data.model_dump())
    if result is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result


@router.put("/{producto_id}/categorias", response_model=List[ProductoCategoriaRead])
def replace_producto_categorias(
    producto_id: int,
    data: List[CategoriaAsignada],
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK))
):
    """Replace all categories for a product atomically. Admin or Stock only."""
    result = ProductoService.reemplazar_categorias(
        session, producto_id, [cat.model_dump() for cat in data]
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result


@router.delete("/{producto_id}/categorias/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_producto_categoria(
    producto_id: int,
    categoria_id: int,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK))
):
    """Remove a category from a product. Admin or Stock only."""
    if not ProductoService.remove_categoria(session, producto_id, categoria_id):
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    return None