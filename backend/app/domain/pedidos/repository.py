# Pedido Repository
from typing import List, Optional, Tuple
from datetime import datetime
from sqlmodel import Session, select, func
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.core.repositories.base import BaseRepository
from app.models.pedido import Pedido
from app.models.producto import Producto
from app.models.detalle_pedido import DetallePedido
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.models.usuario import Usuario


class PedidoRepository(BaseRepository[Pedido]):
    """Repository for Pedido model with order-specific operations."""

    def __init__(self, session: Session):
        super().__init__(Pedido, session)

    def get_all_by_usuario(self, usuario_id: int) -> List[Pedido]:
        """Get all orders for a specific user, newest first."""
        statement = select(Pedido).where(
            Pedido.usuario_id == usuario_id,
        ).order_by(Pedido.created_at.desc())
        return list(self.session.exec(statement))

    def get_all_by_usuario_paginated(
        self,
        usuario_id: int,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Pedido], int]:
        """Get paginated orders for a specific user with optional estado filter."""
        query = select(Pedido).where(Pedido.usuario_id == usuario_id)
        count_query = select(func.count(Pedido.id)).where(Pedido.usuario_id == usuario_id)

        if estado:
            query = query.where(Pedido.estado_codigo == estado)
            count_query = count_query.where(Pedido.estado_codigo == estado)

        query = query.order_by(Pedido.created_at.desc()).offset(skip).limit(limit)

        total = self.session.exec(count_query).one()
        items = list(self.session.exec(query))
        return items, total

    def get_all_paginated(
        self,
        estado: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        busqueda: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[Pedido], int]:
        """Get paginated orders with advanced filters for admin/roles PEDIDOS.
        
        Args:
            estado: Filter by state code.
            desde: Filter by created_at >= desde.
            hasta: Filter by created_at <= hasta.
            busqueda: Search by client name (matches nombre or apellido).
            skip: Offset for pagination.
            limit: Page size.
            
        Returns:
            Tuple of (list of Pedido with usuario loaded, total count).
        """
        base_query = select(Pedido)
        count_query = select(func.count(Pedido.id))

        # Join with Usuario for name search
        if busqueda:
            base_query = base_query.join(Usuario, Pedido.usuario_id == Usuario.id)
            count_query = count_query.join(Usuario, Pedido.usuario_id == Usuario.id)

        if estado:
            base_query = base_query.where(Pedido.estado_codigo == estado)
            count_query = count_query.where(Pedido.estado_codigo == estado)

        if desde:
            base_query = base_query.where(Pedido.created_at >= desde)
            count_query = count_query.where(Pedido.created_at >= desde)

        if hasta:
            base_query = base_query.where(Pedido.created_at <= hasta)
            count_query = count_query.where(Pedido.created_at <= hasta)

        if busqueda:
            search_pattern = f"%{busqueda}%"
            name_filter = or_(
                Usuario.nombre.ilike(search_pattern),
                Usuario.apellido.ilike(search_pattern),
            )
            base_query = base_query.where(name_filter)
            count_query = count_query.where(name_filter)

        # Eagerly load usuario for nombre display
        base_query = base_query.options(joinedload(Pedido.usuario))

        base_query = base_query.order_by(Pedido.created_at.desc()).offset(skip).limit(limit)

        total = self.session.exec(count_query).one()
        items = list(self.session.exec(base_query).unique())
        return items, total

    def get_by_id_with_relations(self, pedido_id: int) -> Optional[Pedido]:
        """Get a single order with all relations eagerly loaded."""
        from sqlalchemy.orm import selectinload

        statement = (
            select(Pedido)
            .options(
                selectinload(Pedido.detalles),
                selectinload(Pedido.historial_estados),
                selectinload(Pedido.usuario),
            )
            .where(Pedido.id == pedido_id)
        )
        return self.session.exec(statement).first()

    def verificar_stock(self, producto_id: int, cantidad: int) -> bool:
        """Check if a product has sufficient stock.

        Uses SELECT ... FOR UPDATE on PostgreSQL to lock the row
        and prevent race conditions (RN-PE04). Falls back to plain
        SELECT on SQLite.
        """
        stmt = select(Producto).where(Producto.id == producto_id)

        # Apply FOR UPDATE on PostgreSQL for race-condition safety
        dialect = self.session.bind.dialect.name if self.session.bind else "sqlite"
        if dialect == "postgresql":
            stmt = stmt.with_for_update()

        producto = self.session.exec(stmt).first()
        if not producto or not producto.disponible:
            return False
        return producto.stock_cantidad >= cantidad

    def decrementar_stock(self, producto_id: int, cantidad: int) -> None:
        """Decrement stock for a product atomically."""
        stmt = select(Producto).where(Producto.id == producto_id)
        dialect = self.session.bind.dialect.name if self.session.bind else "sqlite"
        if dialect == "postgresql":
            stmt = stmt.with_for_update()

        producto = self.session.exec(stmt).first()
        if producto:
            producto.stock_cantidad -= cantidad
            self.session.add(producto)

    def crear_pedido_completo(
        self,
        pedido: Pedido,
        detalles: List[DetallePedido],
        historial: HistorialEstadoPedido,
    ) -> Pedido:
        """Create an order atomically with all its details and initial history entry.

        All operations happen within the same transaction managed by the UoW.
        The caller is responsible for committing the transaction.
        """
        self.session.add(pedido)
        self.session.flush()  # Flush to get pedido.id

        # Set pedido_id for each detail and add
        for detalle in detalles:
            detalle.pedido_id = pedido.id
            self.session.add(detalle)

        # Set pedido_id for history and add
        historial.pedido_id = pedido.id
        self.session.add(historial)

        self.session.flush()
        self.session.refresh(pedido)
        return pedido

    def get_historial_by_pedido_id(self, pedido_id: int) -> List[HistorialEstadoPedido]:
        """Get the chronological audit trail for an order.

        Returns all state transition history entries ordered by creation time.
        The result is a list of append-only HistorialEstadoPedido records.

        Args:
            pedido_id: Order ID.

        Returns:
            List of HistorialEstadoPedido ordered by created_at ascending.
        """
        stmt = (
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.created_at)
        )
        return list(self.session.exec(stmt).all())
