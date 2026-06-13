# Cocina Repository — KDS-specific database queries
from sqlmodel import Session, text

from app.models.pedido import Pedido


class CocinaRepository:
    """Repository for kitchen-display-specific read queries.

    Every query is scoped to orders in CONFIRMADO or EN_PREPARACION
    (the two states visible on the KDS), ordered by age so the oldest
    pending orders appear first.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def listar_pedidos_cocina(self) -> list[Pedido]:
        """Return all orders visible in the KDS, oldest first.

        Filters to orders whose ``estado_codigo`` is either ``CONFIRMADO``
        or ``EN_PREPARACION`` and sorts by ``updated_at`` ascending so that
        orders that have been waiting the longest appear first.

        Returns:
            A list of ``Pedido`` model instances with their ``detalles``
            relationship loaded.
        """
        from sqlalchemy.orm import selectinload
        from sqlmodel import select

        stmt = (
            select(Pedido)
            .options(selectinload(Pedido.detalles))
            .where(Pedido.estado_codigo.in_(["CONFIRMADO", "EN_PREPARACION"]))
            .order_by(Pedido.updated_at.asc())
        )
        return list(self.session.exec(stmt))

    def listar_pedidos_con_tiempo(self) -> dict[int, int]:
        """Return a dict mapping pedido_id -> tiempo_en_cocina_segundos for all kitchen orders.

        Computes the elapsed time in Python using the most recent CONFIRMADO transition
        as reference, falling back to the order's created_at if no history entry exists.
        """
        from datetime import datetime, timezone
        from app.models.historial_estado_pedido import HistorialEstadoPedido
        from sqlmodel import select

        # 1. Get all kitchen pedidos
        stmt = select(Pedido).where(
            Pedido.estado_codigo.in_(["CONFIRMADO", "EN_PREPARACION"]),
        )
        pedidos = self.session.exec(stmt).all()

        if not pedidos:
            return {}

        # 2. Fetch most recent CONFIRMADO transition per pedido (batch query)
        pedido_ids = [p.id for p in pedidos]
        historial_stmt = (
            select(HistorialEstadoPedido)
            .where(
                HistorialEstadoPedido.pedido_id.in_(pedido_ids),
                HistorialEstadoPedido.estado_hacia == "CONFIRMADO",
            )
            .order_by(HistorialEstadoPedido.created_at.desc())
        )
        historiales = self.session.exec(historial_stmt).all()

        # 3. Keep only the latest CONFIRMADO transition per pedido
        latest_confirmed: dict[int, datetime] = {}
        for h in historiales:
            if h.pedido_id not in latest_confirmed:
                latest_confirmed[h.pedido_id] = h.created_at

        # 4. Compute elapsed seconds in Python
        now = datetime.now(timezone.utc)
        result: dict[int, int] = {}
        for p in pedidos:
            ref_time = latest_confirmed.get(p.id, p.created_at)
            # Normalise to aware UTC (model stores naive UTC via utcnow())
            if ref_time.tzinfo is None:
                ref_time = ref_time.replace(tzinfo=timezone.utc)
            result[p.id] = int((now - ref_time).total_seconds())

        return result


