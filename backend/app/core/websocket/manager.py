# ConnectionManager — in-process pub/sub for WebSocket connections
import asyncio
import logging
from typing import Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """In-process pub/sub manager for WebSocket connections.

    Maintains a thread-safe (asyncio) set of active connections and
    broadcasts JSON-serializable events to all connected clients.
    Dead connections are silently pruned during broadcast.

    The singleton instance ``manager`` is importable from the package::

        from app.core.websocket.manager import manager
        await manager.broadcast({"type": "PEDIDO_CONFIRMADO", ...})
    """

    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection and add it to the set.

        Args:
            websocket: The WebSocket to register. Must have been accepted
                       already (or will be accepted here).
        """
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        logger.info("WebSocket connected. Total: %d", len(self._connections))

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection from the set.

        Args:
            websocket: The WebSocket to unregister.
        """
        async with self._lock:
            self._connections.discard(websocket)
        logger.info("WebSocket disconnected. Total: %d", len(self._connections))

    async def broadcast(self, message: dict) -> None:
        """Broadcast a JSON-serializable dict to every connected client.

        Dead connections (those that raised on ``send_json``) are silently
        removed during the broadcast so the caller does not need to worry
        about cleaning them up individually.

        Args:
            message: A dict that will be serialised as JSON and sent to
                     every connected WebSocket.
        """
        dead: list[WebSocket] = []
        async with self._lock:
            for ws in list(self._connections):
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)

            for ws in dead:
                self._connections.discard(ws)

        if dead:
            logger.warning("Removed %d dead connection(s) during broadcast", len(dead))

    @property
    def active_count(self) -> int:
        """Return the number of currently active connections."""
        return len(self._connections)


# Singleton instance — importable from anywhere in the application.
manager = ConnectionManager()
