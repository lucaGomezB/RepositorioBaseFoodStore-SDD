# Admin Router — endpoints protegidos para dashboard administrativo
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.core.database import get_db
from app.core.uow import UnitOfWork
from app.core.auth.deps import TokenPayload
from app.core.auth.authorization import require_roles
from app.core.auth.roles import Role
from app.domain.usuarios.repository import UsuarioRepository
from app.domain.productos.repository import ProductoRepository
from app.domain.usuarios.schemas import UsuarioRead, UsuarioUpdate, UsuarioRoleUpdate
from app.domain.pedidos.schemas import (
    AdminPedidoDetail,
    PedidoListResponse,
)
from app.domain.admin.schemas import (
    ConfigRead,
    ConfigUpdateRequest,
    MetricasResumen,
    VentaPeriodo,
    ProductoRanking,
    PedidoEstadoDistribucion,
    UsuarioListResponse,
    MessageResponse,
)
from app.domain.productos.schemas import ProductoRead
from app.domain.pedidos.service import PedidoService
from app.domain.admin.service import ConfiguracionService
from app.models import Pedido, DetallePedido, EstadoPedido, Usuario, Producto

# --- Sub-routers with specific admin tags ---
dashboard_router = APIRouter(prefix="/admin", tags=["Admin / Dashboard"])
orders_router = APIRouter(prefix="/admin", tags=["Admin / Orders"])
users_router = APIRouter(prefix="/admin", tags=["Admin / Users"])
stock_router = APIRouter(prefix="/admin", tags=["Admin / Stock"])
config_router = APIRouter(prefix="/admin", tags=["Admin / Config"])


@dashboard_router.get("/metricas/resumen", response_model=MetricasResumen)
def metricas_resumen(
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
):
    """Return summary KPIs for the admin dashboard.

    Returns:
        total_ventas: Sum of all completed/confirmed orders.
        pedidos_por_estado: Count of orders grouped by state.
        total_usuarios: Total registered users.
        top_productos: Top 5 most-sold products by quantity.
    """
    with UnitOfWork(session) as uow:
        # Total sales from confirmed/delivered orders
        total_ventas = uow.session.exec(
            select(func.sum(Pedido.total)).where(
                Pedido.estado_codigo.in_(["ENTREGADO", "CONFIRMADO"]),
            ),
        ).one()
        total_ventas = float(total_ventas) if total_ventas else 0

        # Orders per status — includes states with zero orders via LEFT JOIN
        pedidos_por_estado_rows = uow.session.exec(
            select(
                EstadoPedido.codigo,
                EstadoPedido.nombre,
                func.count(Pedido.id).label("cantidad"),
            )
            .outerjoin(Pedido, Pedido.estado_codigo == EstadoPedido.codigo)
            .group_by(EstadoPedido.codigo, EstadoPedido.nombre)
            .order_by(EstadoPedido.codigo),
        ).all()

        # Total registered users
        total_usuarios = uow.session.exec(select(func.count(Usuario.id))).one()

        # Top 5 products by total quantity sold (confirmed/delivered only)
        top_productos_rows = uow.session.exec(
            select(
                Producto.nombre,
                func.sum(DetallePedido.cantidad).label("cantidad"),
            )
            .join(DetallePedido, DetallePedido.producto_id == Producto.id)
            .join(Pedido)
            .where(Pedido.estado_codigo.in_(["ENTREGADO", "CONFIRMADO"]))
            .group_by(Producto.id, Producto.nombre)
            .order_by(func.sum(DetallePedido.cantidad).desc())
            .limit(5),
        ).all()

        return {
        "total_ventas": total_ventas,
        "pedidos_por_estado": [
            {
                "codigo": row.codigo,
                "nombre": row.nombre,
                "cantidad": row.cantidad,
            }
            for row in pedidos_por_estado_rows
        ],
        "total_usuarios": total_usuarios,
        "top_productos": [
            {
                "nombre": row.nombre,
                "cantidad": int(row.cantidad),
            }
            for row in top_productos_rows
        ],
    }


@dashboard_router.get("/metricas/ventas", response_model=list[VentaPeriodo])
def metricas_ventas(
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
    desde: Optional[datetime] = Query(None, description="Start date (inclusive)"),
    hasta: Optional[datetime] = Query(None, description="End date (inclusive)"),
    granularidad: str = Query(
        "dia", pattern="^(dia|semana|mes)$",
        description="Aggregation period: dia, semana, or mes",
    ),
):
    """Aggregated sales over time grouped by day/week/month.

    Only includes confirmed and delivered orders.
    Supports optional date range filtering via `desde` and `hasta`.
    """
    with UnitOfWork(session) as uow:
        # Base filters
        filters = [Pedido.estado_codigo.in_(["ENTREGADO", "CONFIRMADO"])]
        if desde:
            filters.append(Pedido.created_at >= desde)
        if hasta:
            filters.append(Pedido.created_at <= hasta)

        # DATE_TRUNC is PostgreSQL native — works with the configured DATABASE_URL
        periodo = func.date_trunc(granularidad, Pedido.created_at)

        rows = uow.session.exec(
            select(
                periodo.label("periodo"),
                func.sum(Pedido.total).label("total"),
            )
            .where(*filters)
            .group_by(periodo)
            .order_by(periodo),
        ).all()

        return [
            {
                "periodo": row.periodo.isoformat(),
                "total": float(row.total),
            }
            for row in rows
        ]


@dashboard_router.get("/metricas/productos-top", response_model=list[ProductoRanking])
def metricas_productos_top(
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
    top: int = Query(10, ge=1, le=100, description="Number of products to return"),
):
    """Rank products by total quantity sold across all orders.

    Joins DetallePedido with Producto to sum quantities per product.
    """
    with UnitOfWork(session) as uow:
        rows = uow.session.exec(
            select(
                Producto.nombre,
                func.sum(DetallePedido.cantidad).label("cantidad"),
            )
            .join(DetallePedido, DetallePedido.producto_id == Producto.id)
            .join(Pedido)
            .group_by(Producto.id, Producto.nombre)
            .order_by(func.sum(DetallePedido.cantidad).desc())
            .limit(top),
        ).all()

        return [
            {
                "nombre": row.nombre,
                "cantidad": int(row.cantidad),
            }
            for row in rows
        ]


@dashboard_router.get("/metricas/pedidos-por-estado", response_model=list[PedidoEstadoDistribucion])
def metricas_pedidos_por_estado(
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
):
    """Distribution of orders grouped by estado_codigo with state names.

    Uses LEFT JOIN so states with zero orders still appear in the result.
    """
    with UnitOfWork(session) as uow:
        rows = uow.session.exec(
            select(
                EstadoPedido.codigo,
                EstadoPedido.nombre,
                func.count(Pedido.id).label("cantidad"),
            )
            .outerjoin(Pedido, Pedido.estado_codigo == EstadoPedido.codigo)
            .group_by(EstadoPedido.codigo, EstadoPedido.nombre)
            .order_by(EstadoPedido.codigo),
        ).all()

        return [
            {
                "codigo": row.codigo,
                "nombre": row.nombre,
                "cantidad": row.cantidad,
            }
            for row in rows
        ]


@stock_router.get("/productos/stock-bajo", response_model=list[ProductoRead])
def productos_stock_bajo(
    limite: int = Query(10, description="Stock menor a este valor"),
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK)),
):
    """Get products with stock below threshold, sorted by stock ascending.

    Only returns non-deleted products.
    """
    with UnitOfWork(session) as uow:
        repo = ProductoRepository(uow.session)
        productos = repo.get_all(skip=0, limit=100)
        bajo_stock = [p for p in productos if p.stock_cantidad < limite and p.eliminado_en is None]
        bajo_stock.sort(key=lambda p: p.stock_cantidad)
        return bajo_stock


# ---------------------------------------------------------------------------
# Admin Pedidos — listado con datos del usuario
# ---------------------------------------------------------------------------


@orders_router.get("/pedidos/", response_model=PedidoListResponse)
def listar_admin_pedidos(
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.PEDIDOS)),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    estado: Optional[str] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    busqueda: Optional[str] = Query(None),
):
    """List all orders with pagination, filters, and user info (name + email).

    Returns orders ordered by creation date descending, with each item
    including the user's full name and email address.
    Only accessible by ADMIN and PEDIDOS roles.
    """
    with UnitOfWork(session) as uow:
        items, total = PedidoService.listar_pedidos_admin(
            uow,
        estado=estado,
        desde=desde,
        hasta=hasta,
        busqueda=busqueda,
        skip=skip,
        limit=limit,
    )
    return PedidoListResponse(items=items, total_count=total)


@orders_router.get("/pedidos/{pedido_id}", response_model=AdminPedidoDetail)
def obtener_admin_pedido(
    pedido_id: int,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN, Role.PEDIDOS)),
):
    """Get full order detail with user contact info (email, phone).

    Returns all order data including line items and state history,
    enriched with the customer's email and phone number.
    Only accessible by ADMIN and PEDIDOS roles.
    """
    from app.domain.pedidos.repository import PedidoRepository

    with UnitOfWork(session) as uow:
        repo = PedidoRepository(uow.session)
        pedido = repo.get_by_id_with_relations(pedido_id)

        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )

        # Build AdminPedidoDetail from ORM and enrich with user contact data
        detail = AdminPedidoDetail.model_validate(pedido)
        if pedido.usuario:
            detail.usuario_nombre = f"{pedido.usuario.nombre} {pedido.usuario.apellido}"
            detail.usuario_email = pedido.usuario.email
            detail.usuario_telefono = pedido.usuario.telefono

    return detail


# ---------------------------------------------------------------------------
# Admin Usuarios CRUD
# ---------------------------------------------------------------------------


@users_router.get("/usuarios", response_model=UsuarioListResponse)
def listar_usuarios(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    search: Optional[str] = Query(None, description="Search by nombre, apellido, or email"),
    rol_id: Optional[int] = Query(None, description="Filter by role ID"),
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
):
    """List users with pagination, search, and role filtering.

    Excludes soft-deleted users. Returns a dict with items and total count.
    """
    with UnitOfWork(session) as uow:
        repo = UsuarioRepository(uow.session)
        items, total = repo.get_paginated(
            skip=skip, limit=limit, search=search, rol_id=rol_id,
        )
        return {
            "items": [UsuarioRead.model_validate(u).model_dump() for u in items],
            "total": total,
            "skip": skip,
            "limit": limit,
        }


@users_router.put("/usuarios/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(
    usuario_id: int,
    data: UsuarioUpdate,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
):
    """Update user's nombre, apellido, and/or activo.

    Only provided fields are updated. Email is never changed via this endpoint.
    """
    with UnitOfWork(session) as uow:
        repo = UsuarioRepository(uow.session)
        user = repo.get(usuario_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        # Build update dict from non-None fields
        updates = {}
        for field in ("nombre", "apellido", "activo"):
            value = getattr(data, field, None)
            if value is not None:
                updates[field] = value

        if updates:
            user = repo.update(usuario_id, updates)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado",
                )

        uow.session.refresh(user)
    return user


@users_router.delete("/usuarios/{usuario_id}", response_model=MessageResponse)
def eliminar_usuario(
    usuario_id: int,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
):
    """Soft-delete a user by setting eliminado_en timestamp."""
    with UnitOfWork(session) as uow:
        repo = UsuarioRepository(uow.session)
        user = repo.soft_delete(usuario_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

    return {"message": "Usuario eliminado"}


@users_router.patch("/usuarios/{usuario_id}/restaurar", response_model=UsuarioRead)
def restaurar_usuario(
    usuario_id: int,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
):
    """Restore a soft-deleted user by clearing eliminado_en and reactivating."""
    with UnitOfWork(session) as uow:
        repo = UsuarioRepository(uow.session)
        user = repo.restore(usuario_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

    return user


@users_router.put("/usuarios/{usuario_id}/role", response_model=UsuarioRead)
def asignar_rol_usuario(
    usuario_id: int,
    data: UsuarioRoleUpdate,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
):
    """Assign a role to a user. Admin only.
    
    Implements RN-RB04: prevents removing ADMIN from self if last admin.
    """
    with UnitOfWork(session) as uow:
        repo = UsuarioRepository(uow.session)
        user = repo.get(usuario_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        # RN-RB04: Prevent removing ADMIN from self if last admin
        if data.action == "remove" and data.rol_id == Role.ADMIN.value and usuario_id == current_user.user_id:
            admin_users = repo.get_by_rol(Role.ADMIN.value)
            if len(admin_users) <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove admin role from the last administrator",
                )

        if data.action == "add":
            repo.add_role(usuario_id, data.rol_id)
        elif data.action == "remove":
            repo.remove_role(usuario_id, data.rol_id)

        uow.session.refresh(user)

    return user


# ---------------------------------------------------------------------------
# System Configuration
# ---------------------------------------------------------------------------


@config_router.get("/configuracion", response_model=list[ConfigRead])
def listar_configuracion(
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
):
    """List all system configurations."""
    with UnitOfWork(session) as uow:
        return ConfiguracionService.listar(uow)


@config_router.put("/configuracion", response_model=list[ConfigRead])
def actualizar_configuracion(
    data: ConfigUpdateRequest,
    session: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_roles(Role.ADMIN)),
):
    """Update system configurations."""
    items = [item.model_dump() for item in data.configuraciones]
    with UnitOfWork(session) as uow:
        return ConfiguracionService.actualizar(uow, items, current_user.user_id)
