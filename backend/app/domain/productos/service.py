# Producto Service
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from fastapi import HTTPException, status

if TYPE_CHECKING:
    from app.core.uow import UnitOfWork

from app.models.producto import Producto
from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente
from app.domain.productos.repository import ProductoRepository
from app.domain.categorias.repository import CategoriaRepository
from app.domain.ingredientes.repository import IngredienteRepository


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


class ProductoService:
    """Service for Producto operations."""
    
    @staticmethod
    def create(uow: "UnitOfWork", data: dict) -> Producto:
        """Create a new product with relationships."""
        repo = ProductoRepository(uow.session)

        # Prepare product data
        producto_data = data.copy()
        categorias_ids = producto_data.pop("categorias_ids", [])
        categoria_principal_id = producto_data.pop("categoria_principal_id", None)
        ingredientes_data = producto_data.pop("ingredientes", [])

        # Add timestamps
        now = get_timestamp()
        producto_data["fecha_creacion"] = now
        producto_data["fecha_actualizacion"] = now

        # Create product
        db_producto = Producto(**producto_data)
        repo.create(db_producto)

        # Add category relationships
        if categorias_ids:
            for cat_id in categorias_ids:
                repo.add_categoria_relacion(
                    producto_id=db_producto.id,
                    categoria_id=cat_id,
                    es_principal=(cat_id == categoria_principal_id),
                )

        # Add ingredient relationships
        if ingredientes_data:
            for ing in ingredientes_data:
                repo.add_ingrediente_relacion(
                    producto_id=db_producto.id,
                    ingrediente_id=ing["ingrediente_id"],
                    es_removible=ing.get("es_removible", True),
                    es_principal=ing.get("es_principal", False),
                    orden=ing.get("orden", 0),
                )

        # Refresh to get final state
        uow.session.refresh(db_producto)
        return db_producto
    
    @staticmethod
    def get_all(
        uow: "UnitOfWork",
        skip: int = 0,
        limit: int = 100,
        categoria_id: Optional[int] = None,
        busqueda: Optional[str] = None,
        disponible: Optional[bool] = None,
        incluir_eliminados: bool = False,
    ):
        """Get all products with optional filters."""
        from sqlmodel import select
        from app.models.producto_categoria import ProductoCategoria
        
        repo = ProductoRepository(uow.session)
        # Get all (including soft-deleted if requested)
        productos = repo.get_all(skip=skip, limit=limit, incluir_eliminados=incluir_eliminados)
        
        # Apply categoria_id filter by querying the link table
        if categoria_id is not None:
            cat_stmt = select(ProductoCategoria.producto_id).where(
                ProductoCategoria.categoria_id == categoria_id,
            )
            cat_product_ids = set(uow.session.exec(cat_stmt).all())
            productos = [p for p in productos if p.id in cat_product_ids]
        
        # Apply busqueda filter (nombre ILIKE / contains, case-insensitive)
        if busqueda:
            busqueda_lower = busqueda.lower()
            productos = [
                p for p in productos
                if busqueda_lower in p.nombre.lower()
            ]
        
        # Apply disponible filter
        if disponible is not None:
            productos = [p for p in productos if p.disponible == disponible]
        
        return productos
    
    @staticmethod
    def get_by_id(uow: "UnitOfWork", producto_id: int):
        """Get product by ID."""
        repo = ProductoRepository(uow.session)
        return repo.get(producto_id)

    @staticmethod
    def get_catalogo(
        uow: "UnitOfWork",
        page: int = 1,
        limit: int = 20,
        categoria_id: Optional[int] = None,
        busqueda: Optional[str] = None,
        disponible: Optional[bool] = None,
        excluir_alergenos: Optional[str] = None,
    ):
        """Get public catalog products with pagination and filters.

        Returns:
            Tuple of (list of product dicts with hay_stock, total_count).
        """
        from sqlmodel import select
        from app.models.producto_categoria import ProductoCategoria

        repo = ProductoRepository(uow.session)

        # Fetch all matching products (without pagination) for accurate total_count
        all_productos = repo.get_all(
            skip=0,
            limit=10_000_000,
            excluir_alergenos=excluir_alergenos,
        )

        # Apply categoria_id filter by querying the link table
        if categoria_id is not None:
            cat_stmt = select(ProductoCategoria.producto_id).where(
                ProductoCategoria.categoria_id == categoria_id,
            )
            cat_product_ids = set(uow.session.exec(cat_stmt).all())
            all_productos = [p for p in all_productos if p.id in cat_product_ids]

        # Apply busqueda filter (nombre contains, case-insensitive)
        if busqueda:
            busqueda_lower = busqueda.lower()
            all_productos = [
                p for p in all_productos
                if busqueda_lower in p.nombre.lower()
            ]

        # Apply disponible filter
        if disponible is not None:
            all_productos = [p for p in all_productos if p.disponible == disponible]

        total_count = len(all_productos)

        # Paginate
        skip = (page - 1) * limit
        productos_page = all_productos[skip:skip + limit]

        # Convert to dicts with hay_stock
        result = []
        for p in productos_page:
            result.append({
                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio_base": p.precio_base,
                "imagenes_url": p.imagenes_url,
                "tiempo_prep_min": p.tiempo_prep_min,
                "disponible": p.disponible,
                "hay_stock": p.stock_cantidad > 0,
                "fecha_creacion": p.fecha_creacion,
                "fecha_actualizacion": p.fecha_actualizacion,
            })

        return result, total_count

    @staticmethod
    def get_detalle_publico(uow: "UnitOfWork", producto_id: int):
        """Get public product detail with ingredients (including es_alergeno),
        categories, and hay_stock instead of stock_cantidad.

        Returns:
            Dict with ProductoCatalogoRead fields, or None if not found or not available.
        """
        repo = ProductoRepository(uow.session)
        producto = repo.get(producto_id)

        if not producto or not producto.disponible or producto.eliminado_en:
            return None

        ingredientes = repo.get_ingredientes(producto_id)
        categorias = repo.get_categorias(producto_id)

        return {
            "id": producto.id,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "precio_base": producto.precio_base,
            "imagenes_url": producto.imagenes_url,
            "tiempo_prep_min": producto.tiempo_prep_min,
            "disponible": producto.disponible,
            "hay_stock": producto.stock_cantidad > 0,
            "fecha_creacion": producto.fecha_creacion,
            "fecha_actualizacion": producto.fecha_actualizacion,
            "ingredientes": ingredientes,
            "categorias": categorias,
        }
    
    @staticmethod
    def update(uow: "UnitOfWork", producto_id: int, data: dict):
        """Update a product."""
        repo = ProductoRepository(uow.session)
        
        db_producto = repo.get(producto_id)
        if not db_producto:
            return None
        
        # Update fields
        values = {k: v for k, v in data.items() if v is not None}
        values["fecha_actualizacion"] = get_timestamp()
        
        for key, value in values.items():
            if key not in ["categorias_ids", "categoria_principal_id", "ingredientes"]:
                setattr(db_producto, key, value)
        
        uow.session.add(db_producto)
        uow.session.flush()
        uow.session.refresh(db_producto)
        return db_producto
    
    @staticmethod
    def delete(uow: "UnitOfWork", producto_id: int):
        """Soft delete a product."""
        repo = ProductoRepository(uow.session)
        producto = repo.soft_delete(producto_id)
        if producto:
            uow.session.flush()
        return producto
    
    @staticmethod
    def get_ingredientes(uow: "UnitOfWork", producto_id: int):
        """Get product ingredients."""
        repo = ProductoRepository(uow.session)
        return repo.get_ingredientes(producto_id)
    
    @staticmethod
    def get_categorias(uow: "UnitOfWork", producto_id: int):
        """Get product categories."""
        repo = ProductoRepository(uow.session)
        return repo.get_categorias(producto_id)
    
    @staticmethod
    def actualizar_stock(uow: "UnitOfWork", producto_id: int, cantidad: int):
        """
        Atomically update stock quantity.
        
        Args:
            uow: Unit of Work transaction wrapper.
            producto_id: Product ID
            cantidad: Delta to apply (positive to increment, negative to decrement)
            
        Returns:
            Updated Producto if successful
            
        Raises:
            HTTPException 404 if product not found
            HTTPException 400 if insufficient stock
        """
        repo = ProductoRepository(uow.session)
        producto, was_updated = repo.actualizar_stock(producto_id, cantidad)
        
        if producto is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )
        
        if not was_updated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock",
            )
        
        return producto
    
    @staticmethod
    def add_ingrediente(uow: "UnitOfWork", producto_id: int, data: dict):
        """Add ingredient to product."""
        from sqlalchemy.exc import IntegrityError
        
        repo = ProductoRepository(uow.session)
        db_producto = repo.get(producto_id)
        if not db_producto:
            return None
        
        try:
            repo.add_ingrediente_relacion(
                producto_id=producto_id,
                ingrediente_id=data["ingrediente_id"],
                es_removible=data.get("es_removible", True),
                es_principal=data.get("es_principal", False),
                orden=data.get("orden", 0),
            )
            
            return repo.get_ingredientes(producto_id)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esa relación ingrediente-producto ya existe",
            )
    
    @staticmethod
    def remove_ingrediente(uow: "UnitOfWork", producto_id: int, ingrediente_id: int):
        """Remove ingredient from product."""
        repo = ProductoRepository(uow.session)
        result = repo.delete_ingrediente_relacion(producto_id, ingrediente_id)
        return result
    
    @staticmethod
    def add_categoria(uow: "UnitOfWork", producto_id: int, data: dict):
        """Add category to product."""
        from sqlalchemy.exc import IntegrityError
        
        repo = ProductoRepository(uow.session)
        db_producto = repo.get(producto_id)
        if not db_producto:
            return None
        
        try:
            repo.add_categoria_relacion(
                producto_id=producto_id,
                categoria_id=data["categoria_id"],
                es_principal=data.get("es_principal", False),
            )
            
            return repo.get_categorias(producto_id)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esa relación categoría-producto ya existe",
            )
    
    @staticmethod
    def remove_categoria(uow: "UnitOfWork", producto_id: int, categoria_id: int):
        """Remove category from product."""
        repo = ProductoRepository(uow.session)
        result = repo.delete_categoria_relacion(producto_id, categoria_id)
        return result

    @staticmethod
    def reemplazar_ingredientes(uow: "UnitOfWork", producto_id: int, ingredientes: list[dict]):
        """Replace all ingredients for a product atomically.

        Deletes all existing ingredient relationships and inserts new ones.
        """
        repo = ProductoRepository(uow.session)

        # Verify product exists
        db_producto = repo.get(producto_id)
        if not db_producto:
            return None

        # Delete all existing relationships
        repo.delete_all_ingrediente_relaciones(producto_id)
        # Flush so DELETE hits DB before INSERT
        uow.session.flush()

        # Insert new relationships
        for ing in ingredientes:
            repo.add_ingrediente_relacion(
                producto_id=producto_id,
                ingrediente_id=ing["ingrediente_id"],
                es_removible=ing.get("es_removible", True),
                es_principal=ing.get("es_principal", False),
                orden=ing.get("orden", 0),
            )

        return repo.get_ingredientes(producto_id)

    @staticmethod
    def reemplazar_categorias(uow: "UnitOfWork", producto_id: int, categorias: list[dict]):
        """Replace all categories for a product atomically.

        Deletes all existing category relationships and inserts new ones.
        """
        repo = ProductoRepository(uow.session)

        # Verify product exists
        db_producto = repo.get(producto_id)
        if not db_producto:
            return None

        # Delete all existing relationships
        repo.delete_all_categoria_relaciones(producto_id)
        # Flush so DELETE hits DB before INSERT
        uow.session.flush()

        # Insert new relationships
        for cat in categorias:
            repo.add_categoria_relacion(
                producto_id=producto_id,
                categoria_id=cat["categoria_id"],
                es_principal=cat.get("es_principal", False),
            )

        return repo.get_categorias(producto_id)
