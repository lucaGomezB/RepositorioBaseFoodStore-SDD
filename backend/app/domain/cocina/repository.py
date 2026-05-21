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
        """Return a dict mapping pedido_id -> tiempo_en_cocina_segundos for all kitchen orders, single query."""
        sql = text("""
            SELECT p.id,
                   EXTRACT(EPOCH FROM (NOW() - COALESCE(h.created_at, p.created_at)))::int AS tiempo_segundos
            FROM pedidos p
            LEFT JOIN LATERAL (
                SELECT created_at FROM historial_estados_pedido
                WHERE pedido_id = p.id AND estado_hacia = 'CONFIRMADO'
                ORDER BY created_at DESC LIMIT 1
            ) h ON true
            WHERE p.estado_codigo IN ('CONFIRMADO', 'EN_PREPARACION')
        """)
        result: dict[int, int] = {}
        rows = self.session.exec(sql).all()
        for row in rows:
            pid = int(row[0])
            tiempo = int(row[1])
            result[pid] = tiempo
        return result


