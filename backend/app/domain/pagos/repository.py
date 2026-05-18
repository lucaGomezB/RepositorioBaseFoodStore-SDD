# Pago Repository
from typing import Optional, List
from sqlmodel import Session, select
from app.models.pago import Pago
from app.core.repositories.base import BaseRepository


class PagoRepository(BaseRepository[Pago]):
    """Repository for Pago entity operations."""

    def __init__(self, session: Session):
        super().__init__(Pago, session)

    def get_by_pedido_id(self, pedido_id: int) -> Optional[Pago]:
        """Get the latest payment record for an order."""
        statement = (
            select(Pago)
            .where(Pago.pedido_id == pedido_id)
            .order_by(Pago.created_at.desc())
            .limit(1)
        )
        return self.session.exec(statement).first()

    def get_all_by_pedido_id(self, pedido_id: int) -> List[Pago]:
        """Get all payment records for an order (for retry history)."""
        statement = (
            select(Pago)
            .where(Pago.pedido_id == pedido_id)
            .order_by(Pago.created_at.desc())
        )
        return list(self.session.exec(statement))

    def get_by_mp_payment_id(self, mp_payment_id: int) -> Optional[Pago]:
        """Get payment by MercadoPago payment ID."""
        statement = select(Pago).where(Pago.mp_payment_id == mp_payment_id)
        return self.session.exec(statement).first()

    def get_by_idempotency_key(self, key: str) -> Optional[Pago]:
        """Get payment by idempotency key (for duplicate prevention)."""
        statement = select(Pago).where(Pago.idempotency_key == key)
        return self.session.exec(statement).first()

    def get_by_external_reference(self, ref: str) -> Optional[Pago]:
        """Get payment by external reference."""
        statement = select(Pago).where(Pago.external_reference == ref)
        return self.session.exec(statement).first()
