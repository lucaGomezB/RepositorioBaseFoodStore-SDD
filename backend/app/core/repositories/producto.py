# Producto Repository
from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session, select, text
from app.core.repositories.base import BaseRepository
from app.models.producto import Producto
from app.models.producto_categoria import ProductoCategoria
from app.models.producto_ingrediente import ProductoIngrediente
from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente


class ProductoRepository(BaseRepository[Producto]):
    """Repository for Producto model."""
    
    def __init__(self, session: Session):
        super().__init__(Producto, session)
    
    def get(self, id: int) -> Optional[Producto]:
        """Get product by ID, excluding soft-deleted by default."""
        statement = select(Producto).where(
            Producto.id == id,
            Producto.eliminado_en.is_(None),
        )
        return self.session.exec(statement).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        incluir_eliminados: bool = False,
        excluir_alergenos: Optional[str] = None,
    ) -> List[Producto]:
        """Get all products, optionally including soft-deleted.

        Args:
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.
            incluir_eliminados: If True, include soft-deleted products.
            excluir_alergenos: Comma-separated ingredient IDs to exclude.
                Products containing ANY of these ingredients will be filtered out.
        """
        statement = select(Producto)
        if not incluir_eliminados:
            statement = statement.where(Producto.eliminado_en.is_(None))

        if excluir_alergenos:
            try:
                alergeno_ids = [int(x.strip()) for x in excluir_alergenos.split(",") if x.strip()]
            except ValueError:
                raise ValueError("excluir_alergenos must contain comma-separated integer IDs")

            if alergeno_ids:
                from sqlmodel import exists
                subq = select(ProductoIngrediente.producto_id).where(
                    ProductoIngrediente.ingrediente_id.in_(alergeno_ids),
                    ProductoIngrediente.producto_id == Producto.id,
                )
                statement = statement.where(~exists(subq))

        statement = statement.offset(skip).limit(limit)
        return list(self.session.exec(statement))
    
    def get_with_relations(self, producto_id: int) -> Optional[Producto]:
        """Get product with all relationships loaded."""
        producto = self.get(producto_id)
        if producto:
            # Load relationships
            _ = producto.categorias
            _ = producto.ingredientes
        return producto
    
    def get_disponibles(self, skip: int = 0, limit: int = 100) -> List[Producto]:
        """Get available products."""
        from sqlmodel import col
        statement = select(Producto).where(
            Producto.disponible == True,
            Producto.eliminado_en.is_(None),
        ).offset(skip).limit(limit)
        return list(self.session.exec(statement))
    
    # --- Soft delete ---
    
    def soft_delete(self, producto_id: int) -> Optional[Producto]:
        """Soft delete a product by setting eliminado_en to current timestamp."""
        producto = self.session.get(Producto, producto_id)
        if producto is None:
            return None
        producto.eliminado_en = datetime.now(timezone.utc)
        producto.fecha_actualizacion = datetime.now(timezone.utc).isoformat()
        self.session.add(producto)
        self.session.flush()
        return producto
    
    # --- Atomic stock update ---
    
    def actualizar_stock(self, producto_id: int, delta: int) -> tuple[Optional[Producto], bool]:
        """
        Atomically update stock_cantidad.
        
        Uses a single UPDATE with WHERE condition to prevent race conditions.
        
        Returns:
            Tuple of (producto or None, was_updated or insufficient).
            - (Producto, True) if stock was updated successfully.
            - (None, False) if product not found or soft-deleted.
            - (Producto, False) if product exists but stock would go below zero.
        """
        now_ts = datetime.now(timezone.utc).isoformat()
        stmt = text("""
            UPDATE productos
            SET stock_cantidad = stock_cantidad + :delta,
                fecha_actualizacion = :now
            WHERE id = :id
              AND eliminado_en IS NULL
              AND (stock_cantidad + :delta) >= 0
        """)
        result = self.session.exec(stmt, params={
            "id": producto_id,
            "delta": delta,
            "now": now_ts,
        })
        self.session.flush()
        
        if result.rowcount > 0:
            # Update succeeded — refresh and return
            producto = self.session.get(Producto, producto_id)
            self.session.refresh(producto)
            return (producto, True)
        
        # No rows affected — check why
        producto = self.session.get(Producto, producto_id)
        if producto is None or producto.eliminado_en is not None:
            return (None, False)
        
        # Product exists but stock would go below zero
        return (producto, False)
    
    # --- Relationship methods ---
    
    def add_categoria_relacion(self, producto_id: int, categoria_id: int, es_principal: bool = False):
        """Add category relationship."""
        enlace = ProductoCategoria(
            producto_id=producto_id,
            categoria_id=categoria_id,
            es_principal=es_principal,
        )
        self.session.add(enlace)
        return enlace
    
    def add_ingrediente_relacion(
        self,
        producto_id: int,
        ingrediente_id: int,
        es_removible: bool = True,
        es_principal: bool = False,
        orden: int = 0,
    ):
        """Add ingredient relationship."""
        enlace = ProductoIngrediente(
            producto_id=producto_id,
            ingrediente_id=ingrediente_id,
            es_removible=es_removible,
            es_principal=es_principal,
            orden=orden,
        )
        self.session.add(enlace)
        return enlace
    
    def get_ingredientes(self, producto_id: int) -> List[dict]:
        """Get ingredients with relationship data."""
        statement = (
            select(ProductoIngrediente, Ingrediente)
            .join(Ingrediente, ProductoIngrediente.ingrediente_id == Ingrediente.id)
            .where(ProductoIngrediente.producto_id == producto_id)
            .order_by(ProductoIngrediente.orden)
        )
        results = self.session.exec(statement).all()
        return [
            {
                "ingrediente_id": rel.ingrediente_id,
                "ingrediente_nombre": ing.nombre,
                "es_removible": rel.es_removible,
                "es_principal": rel.es_principal,
                "orden": rel.orden,
                "es_alergeno": ing.es_alergeno,
            }
            for rel, ing in results
        ]
    
    def get_categorias(self, producto_id: int) -> List[dict]:
        """Get categories with relationship data."""
        statement = (
            select(ProductoCategoria, Categoria)
            .join(Categoria, ProductoCategoria.categoria_id == Categoria.id)
            .where(ProductoCategoria.producto_id == producto_id)
        )
        results = self.session.exec(statement).all()
        return [
            {
                "categoria_id": rel.categoria_id,
                "categoria_nombre": cat.nombre,
                "es_principal": rel.es_principal,
            }
            for rel, cat in results
        ]
    
    def delete_all_ingrediente_relaciones(self, producto_id: int) -> None:
        """Delete all ingredient relationships for a product."""
        stmt = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id,
        )
        enlaces = self.session.exec(stmt).all()
        for enlace in enlaces:
            self.session.delete(enlace)

    def delete_all_categoria_relaciones(self, producto_id: int) -> None:
        """Delete all category relationships for a product."""
        stmt = select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto_id,
        )
        enlaces = self.session.exec(stmt).all()
        for enlace in enlaces:
            self.session.delete(enlace)

    def delete_ingrediente_relacion(self, producto_id: int, ingrediente_id: int) -> bool:
        """Delete ingredient relationship."""
        statement = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id,
            ProductoIngrediente.ingrediente_id == ingrediente_id,
        )
        enlace = self.session.exec(statement).first()
        if enlace:
            self.session.delete(enlace)
            return True
        return False
    
    def delete_categoria_relacion(self, producto_id: int, categoria_id: int) -> bool:
        """Delete category relationship."""
        statement = select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto_id,
            ProductoCategoria.categoria_id == categoria_id,
        )
        enlace = self.session.exec(statement).first()
        if enlace:
            self.session.delete(enlace)
            return True
        return False