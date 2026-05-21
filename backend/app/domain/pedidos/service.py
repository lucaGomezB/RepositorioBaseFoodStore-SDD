# Pedido Service + FSM (Finite State Machine)
import asyncio
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from fastapi import HTTPException, status

if TYPE_CHECKING:
    from app.core.uow import UnitOfWork

from app.models.pedido import Pedido
from app.domain.pedidos.schemas import PedidoRead
from app.models.detalle_pedido import DetallePedido
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.models.producto import Producto
from app.domain.pedidos.repository import PedidoRepository
from app.domain.direcciones.repository import DireccionRepository
from app.core.repositories.base import BaseRepository
from app.domain.productos.repository import ProductoRepository
from app.core.auth.roles import Role
from app.core.websocket.manager import manager as ws_manager
from app.core.websocket.events import CocinaEvent

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# FSM — State machine map
# ---------------------------------------------------------------------------
# Maps each state to the list of valid target states.
TRANSICIONES = {
    "PENDIENTE": ["CONFIRMADO", "CANCELADO"],
    "CONFIRMADO": ["EN_PREPARACION", "CANCELADO"],
    "EN_PREPARACION": ["EN_CAMINO", "CANCELADO"],
    "EN_CAMINO": ["ENTREGADO"],
    "ENTREGADO": [],
    "CANCELADO": [],
}


def validar_transicion(desde: str, hacia: str) -> bool:
    """Validate whether a state transition is allowed by the FSM.

    Args:
        desde: Current state code.
        hacia: Target state code.

    Returns:
        True if the transition is valid, False otherwise.
    """
    return hacia in TRANSICIONES.get(desde, [])


# ---------------------------------------------------------------------------
# Event helpers for real-time KDS broadcasting
# ---------------------------------------------------------------------------

def _build_event_for_transition(
    pedido: Pedido,
    desde: str,
    hacia: str,
) -> Optional[dict]:
    """Build a CocinaEvent dict for the given FSM transition, or None.

    Only kitchen-relevant transitions (CONFIRMADO, EN_PREPARACION,
    EN_CAMINO, CANCELADO from CONFIRMADO/EN_PREPARACION) produce events.

    Args:
        pedido: The Pedido instance (must have detalles accessible).
        desde: Source state code.
        hacia: Target state code.

    Returns:
        A dict suitable for WebSocket broadcast, or None.
    """
    if desde == "PENDIENTE" and hacia == "CONFIRMADO":
        items_data: list[dict[str, Any]] = []
        for detalle in (pedido.detalles or []):
            items_data.append({
                "producto_id": detalle.producto_id,
                "nombre": detalle.nombre_snapshot,
                "cantidad": detalle.cantidad,
            })
        event = CocinaEvent(
            "PEDIDO_CONFIRMADO",
            pedido.id,
            data={"items": items_data},
        )
        return event.to_dict()

    if desde == "CONFIRMADO" and hacia == "EN_PREPARACION":
        event = CocinaEvent("PEDIDO_EN_PREPARACION", pedido.id)
        return event.to_dict()

    if desde == "EN_PREPARACION" and hacia == "EN_CAMINO":
        event = CocinaEvent("PEDIDO_EN_CAMINO", pedido.id)
        return event.to_dict()

    if hacia == "CANCELADO" and desde in ("CONFIRMADO", "EN_PREPARACION"):
        event = CocinaEvent("PEDIDO_CANCELADO", pedido.id)
        return event.to_dict()

    return None


def _broadcast_event(event_dict: dict) -> None:
    """Dispatch a WebSocket broadcast safely without blocking the caller.

    Works in both sync and async contexts:
    - If a running event loop exists, schedule via ``ensure_future``.
    - Otherwise, create a temporary event loop with ``asyncio.run``.

    All exceptions are caught and logged so the caller transaction is
    never broken by a failing WebSocket broadcast.
    """
    try:
        loop = asyncio.get_running_loop()
        task = asyncio.ensure_future(ws_manager.broadcast(event_dict))
        task.add_done_callback(lambda t: t.exception() and logger.error("Broadcast failed: %s", t.exception()))
    except RuntimeError:
        # No running event loop — create one
        try:
            asyncio.run(ws_manager.broadcast(event_dict))
        except Exception as e:
            logger.warning(
                "Could not broadcast %s: %s",
                event_dict.get("type"), e,
            )
    except Exception:
        logger.exception(
            "Failed to broadcast %s (event ignored)",
            event_dict.get("type"),
        )


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class PedidoService:
    """Service for order operations.

    All business logic is stateless. The database session is injected
    through the repository layer.
    """

    @staticmethod
    def crear_pedido(
        uow: "UnitOfWork",
        usuario_id: int,
        data: dict,
    ) -> Pedido:
        """Create a new order atomically.

        Steps:
        1. Validate stock for each item (SELECT FOR UPDATE on PostgreSQL)
        2. Fetch the user's delivery address and copy snapshots
        3. Create Pedido with PENDIENTE state and address snapshot
        4. Create DetallePedido entries with price/name snapshots
        5. Calculate subtotals and total
        6. Create initial HistorialEstadoPedido (desde=NULL, hacia=PENDIENTE)
        7. Decrement stock for each product
        8. Return the created Pedido with relations loaded

        Args:
            uow: Unit of Work transaction wrapper.
            usuario_id: ID of the user creating the order.
            data: Dictionary with items, forma_pago_codigo, direccion_id.

        Returns:
            The created Pedido instance with details and history.
        """
        repo = PedidoRepository(uow.session)
        producto_repo = BaseRepository(Producto, uow.session)
        direccion_repo = DireccionRepository(uow.session)

        items = data["items"]
        direccion_id = data.get("direccion_id")

        # ------------------------------------------------------------------
        # Step 1: Validate stock for every item
        # ------------------------------------------------------------------
        productos_cache: dict[int, Producto] = {}
        for item in items:
            pid = item["producto_id"]
            cantidad = item["cantidad"]

            if not repo.verificar_stock(pid, cantidad):
                raise ValueError(
                    f"Stock insuficiente para producto_id={pid}. "
                    f"Solicitado: {cantidad}."
                )

            # Fetch full product for snapshot
            if pid not in productos_cache:
                prod = producto_repo.get(pid)
                if not prod:
                    raise ValueError(f"Producto no encontrado: id={pid}")
                productos_cache[pid] = prod

        # ------------------------------------------------------------------
        # Step 2: Fetch delivery address and copy snapshot
        # ------------------------------------------------------------------
        direccion = direccion_repo.get_by_id_and_usuario(direccion_id, usuario_id)
        if not direccion:
            raise ValueError(
                f"Dirección no encontrada o no pertenece al usuario: id={direccion_id}"
            )

        # ------------------------------------------------------------------
        # Step 3: Create Pedido with address snapshot
        # ------------------------------------------------------------------
        now = datetime.now(timezone.utc)
        costo_envio = 50.0  # Fixed for v1 (RN-PE02)

        pedido = Pedido(
            usuario_id=usuario_id,
            estado_codigo="PENDIENTE",
            total=0.0,  # Will be calculated
            costo_envio=costo_envio,
            forma_pago_codigo=data.get("forma_pago_codigo"),
            direccion_calle=direccion.calle,
            direccion_numero=direccion.numero,
            direccion_piso=direccion.piso_depto,
            direccion_ciudad=direccion.ciudad,
            direccion_cp=direccion.codigo_postal,
            latitud=data.get("latitud"),
            longitud=data.get("longitud"),
            created_at=now,
            updated_at=now,
        )

        # ------------------------------------------------------------------
        # Step 4 & 5: Create DetallePedido entries with snapshots + calculate
        # ------------------------------------------------------------------
        detalles: List[DetallePedido] = []
        total = 0.0

        for item in items:
            prod = productos_cache[item["producto_id"]]
            precio = float(prod.precio_base) if hasattr(prod, 'precio_base') else 0.0
            cantidad = item["cantidad"]
            subtotal = round(precio * cantidad, 2)

            detalle = DetallePedido(
                producto_id=prod.id,
                nombre_snapshot=prod.nombre,
                precio_snapshot=precio,
                cantidad=cantidad,
                exclusiones=item.get("exclusiones", []),
                subtotal=subtotal,
            )
            detalles.append(detalle)
            total += subtotal

        total = round(total + costo_envio, 2)
        pedido.total = total

        # ------------------------------------------------------------------
        # Step 6: Create initial HistorialEstadoPedido
        # ------------------------------------------------------------------
        historial = HistorialEstadoPedido(
            estado_desde=None,  # RN-02: first entry has NULL estado_desde
            estado_hacia="PENDIENTE",
            created_at=now,
        )

        # ------------------------------------------------------------------
        # Step 7: Decrement stock
        # ------------------------------------------------------------------
        for item in items:
            repo.decrementar_stock(item["producto_id"], item["cantidad"])

        # ------------------------------------------------------------------
        # Create everything atomically
        # ------------------------------------------------------------------
        pedido_completo = repo.crear_pedido_completo(pedido, detalles, historial)

        return pedido_completo

    @staticmethod
    def obtener_pedido(uow: "UnitOfWork", pedido_id: int, usuario_id: int, is_admin: bool = False) -> Optional[Pedido]:
        """Get an order by ID.

        Regular users can only see their own orders. Admins can see any order.

        Args:
            uow: Unit of Work transaction wrapper.
            pedido_id: Order ID.
            usuario_id: Current user ID.
            is_admin: Whether the current user has admin role.

        Returns:
            Pedido with details and history, or None if not found/not allowed.
        """
        repo = PedidoRepository(uow.session)
        pedido = repo.get_by_id_with_relations(pedido_id)

        if not pedido:
            return None

        # Ownership check: non-admin users can only see their own orders
        if not is_admin and pedido.usuario_id != usuario_id:
            return None

        return pedido

    @staticmethod
    def transicionar_estado(
        uow: "UnitOfWork",
        pedido_id: int,
        nuevo_estado: str,
        usuario_id: Optional[int] = None,
        motivo: Optional[str] = None,
        rol_id: Optional[int] = None,
    ) -> Pedido:
        """Transition an order to a new state following the FSM.

        Validates the transition against the FSM rules, records the
        transition in the append-only history log, and updates the
        order's current state.

        If cancelling from CONFIRMADO, stock is restored atomically.

        After a successful flush, kitchen-relevant transitions are
        broadcast as real-time events to connected WebSocket clients.

        Args:
            uow: Unit of Work transaction wrapper.
            pedido_id: Order ID.
            nuevo_estado: Target state code.
            usuario_id: User performing the transition (for audit trail).
            motivo: Reason for the transition (required for CANCELADO).
            rol_id: Role ID of the user performing the transition.
                     When COCINA, only CONFIRMADO→EN_PREPARACION and
                     EN_PREPARACION→EN_CAMINO are allowed (RN-CO03).

        Returns:
            The updated Pedido instance.

        Raises:
            HTTPException: 404 if order not found.
            HTTPException: 400 if transition is invalid or motivo missing.
            HTTPException: 403 if the role does not have permission
                           for the requested transition (RN-CO03).
        """
        pedido = uow.session.get(Pedido, pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        # Capture source state before any mutation
        desde = pedido.estado_codigo

        if not validar_transicion(desde, nuevo_estado):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transicion {desde} -> {nuevo_estado} no permitida",
            )

        # ------------------------------------------------------------------
        # Role-based transition validation (RN-CO03)
        # ------------------------------------------------------------------
        if rol_id == Role.COCINA.value:
            cocina_permitted = {"CONFIRMADO": ["EN_PREPARACION"], "EN_PREPARACION": ["EN_CAMINO"]}
            allowed = cocina_permitted.get(desde, [])
            if nuevo_estado not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="El rol COCINA no puede ejecutar esta transición",
                )

        if nuevo_estado == "CANCELADO" and not motivo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Motivo obligatorio para cancelacion",
            )

        # Restore stock if cancelling from CONFIRMADO
        if nuevo_estado == "CANCELADO" and desde == "CONFIRMADO":
            producto_repo = ProductoRepository(uow.session)
            for detalle in pedido.detalles:
                producto_repo.actualizar_stock(detalle.producto_id, detalle.cantidad)

        # Record history entry
        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_desde=desde,
            estado_hacia=nuevo_estado,
            motivo=motivo,
            usuario_id=usuario_id,
        )
        uow.session.add(historial)

        # Update order state
        pedido.estado_codigo = nuevo_estado
        pedido.updated_at = datetime.now(timezone.utc)
        uow.session.flush()
        uow.session.refresh(pedido)

        # ------------------------------------------------------------------
        # Schedule real-time event — caller broadcasts after UoW commits
        # ------------------------------------------------------------------
        event_dict = _build_event_for_transition(pedido, desde, nuevo_estado)
        if event_dict:
            pedido._pending_event = event_dict

        return pedido

    @staticmethod
    def obtener_historial(
        uow: "UnitOfWork",
        pedido_id: int,
        usuario_id: int,
        is_admin: bool = False,
    ) -> List[HistorialEstadoPedido]:
        """Get the state transition history for an order.

        Regular users can only see history for their own orders.
        Admins can see history for any order.

        Args:
            uow: Unit of Work transaction wrapper.
            pedido_id: Order ID.
            usuario_id: Current user ID.
            is_admin: Whether the current user has admin role.

        Returns:
            List of HistorialEstadoPedido ordered chronologically.

        Raises:
            HTTPException 404: If the order does not exist or
                the user does not have access to it.
        """
        pedido = uow.session.get(Pedido, pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )
        if not is_admin and pedido.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )
        repo = PedidoRepository(uow.session)
        return repo.get_historial_by_pedido_id(pedido_id)

    @staticmethod
    def listar_pedidos(
        uow: "UnitOfWork",
        usuario_id: int,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple:
        """List paginated orders for a user with optional estado filter.
        
        Returns:
            Tuple of (list of Pedido with items_count set, total_count).
        """
        repo = PedidoRepository(uow.session)
        items, total = repo.get_all_by_usuario_paginated(
            usuario_id, estado=estado, skip=skip, limit=limit,
        )
        # Convert to PedidoRead with items_count
        read_items = []
        for p in items:
            pr = PedidoRead.model_validate(p)
            pr.items_count = len(p.detalles) if p.detalles else 0
            read_items.append(pr)
        return read_items, total

    @staticmethod
    def listar_pedidos_admin(
        uow: "UnitOfWork",
        estado: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        busqueda: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple:
        """List paginated orders with advanced filters for ADMIN/PEDIDOS roles.
        
        Returns:
            Tuple of (list of Pedido with usuario_nombre and items_count set, total_count).
        """
        repo = PedidoRepository(uow.session)
        items, total = repo.get_all_paginated(
            estado=estado, desde=desde, hasta=hasta,
            busqueda=busqueda, skip=skip, limit=limit,
        )
        read_items = []
        for p in items:
            pr = PedidoRead.model_validate(p)
            pr.items_count = len(p.detalles) if p.detalles else 0
            if p.usuario:
                pr.usuario_nombre = f"{p.usuario.nombre} {p.usuario.apellido}"
                pr.usuario_email = p.usuario.email
            read_items.append(pr)
        return read_items, total
