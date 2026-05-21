# Event type definitions for real-time kitchen updates
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime, timezone


@dataclass
class CocinaEvent:
    """Event payload for kitchen display real-time updates.

    Attributes:
        type: Event type identifier (PEDIDO_CONFIRMADO, PEDIDO_EN_PREPARACION,
              PEDIDO_EN_CAMINO, PEDIDO_CANCELADO).
        pedido_id: The order ID that triggered the event.
        data: Arbitrary payload data (e.g., estado_hacia, items count).
        timestamp: UTC timestamp when the event was created.
    """

    type: str
    pedido_id: int
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "pedido_id": self.pedido_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }
