# Cocina Service — Kitchen Display System business logic
from app.domain.cocina.repository import CocinaRepository
from app.domain.cocina.schemas import (
    PedidoCocinaRead,
    PedidoCocinaItem,
    PedidoCocinaListResponse,
)
from app.core.uow import UnitOfWork
from app.models.ingrediente import Ingrediente
from sqlmodel import select


class CocinaService:
    """Stateless service for KDS read operations.

    All database access is injected through ``UnitOfWork``, keeping the
    service testable without a real database connection.
    """

    @staticmethod
    def _resolve_ingredientes_nombres(uow: UnitOfWork, ids: set[int]) -> dict[int, str]:
        """Resolve ingredient IDs to human-readable names in a single query."""
        if not ids:
            return {}
        stmt = select(Ingrediente).where(Ingrediente.id.in_(ids))
        ingredientes = uow.session.exec(stmt).all()
        return {ing.id: ing.nombre for ing in ingredientes}

    @staticmethod
    def listar_pedidos(uow: UnitOfWork) -> PedidoCocinaListResponse:
        """Return all orders visible on the KDS with kitchen timing.

        Iterates over the active kitchen orders (CONFIRMADO and
        EN_PREPARACION) and builds the display representation with
        elapsed time and line-item details.

        Args:
            uow: Unit of Work providing the database session.

        Returns:
            A ``PedidoCocinaListResponse`` containing the ordered items
            and a total count.
        """
        repo = CocinaRepository(uow.session)
        pedidos = repo.listar_pedidos_cocina()
        tiempos_map = repo.listar_pedidos_con_tiempo()

        # Collect all ingredient IDs from all items to resolve names in batch
        all_ids: set[int] = set()
        for p in pedidos:
            for d in (p.detalles or []):
                if d.exclusiones:
                    all_ids.update(d.exclusiones)
        nombres_map = CocinaService._resolve_ingredientes_nombres(uow, all_ids)

        items: list[PedidoCocinaRead] = []
        for p in pedidos:
            tiempo = tiempos_map.get(p.id, 0)

            detalle_items = [
                PedidoCocinaItem(
                    nombre_producto=d.nombre_snapshot,
                    cantidad=d.cantidad,
                    exclusiones=list(d.exclusiones) if d.exclusiones else [],
                    exclusiones_nombres=[nombres_map[eid] for eid in (d.exclusiones or []) if eid in nombres_map],
                )
                for d in (p.detalles or [])
            ]

            items.append(
                PedidoCocinaRead(
                    id=p.id,
                    numero_pedido=p.id,
                    estado_codigo=p.estado_codigo,
                    items=detalle_items,
                    notas=None,  # Pedido model does not have a notas column
                    tiempo_en_cocina_segundos=tiempo,
                    created_at=p.created_at,
                )
            )

        return PedidoCocinaListResponse(items=items, total_count=len(items))
