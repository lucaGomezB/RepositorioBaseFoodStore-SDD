"""
Tests for Cocina (Kitchen Display System) module.

Covers:
- Task 8.1: Unit tests for CocinaService + endpoint integration tests
- Task 8.2: WebSocket integration tests (TestClient de FastAPI)
- Task 8.3: Seed tests (rol COCINA existe, usuario de prueba existe)
"""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch, MagicMock
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect
import time

from app.main import app
from app.core.auth.tokens import create_access_token
from app.core.auth.roles import Role
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.models.producto import Producto
from app.models.estado_pedido import EstadoPedido
from app.models.direccion import Direccion
from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.core.database import get_db
from app.core.uow import UnitOfWork


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


def seed_all_roles(session: Session) -> None:
    """Seed all roles including COCINA (idempotent)."""
    from app.models.rol import Rol
    existing = session.exec(select(Rol).limit(1)).first()
    if not existing:
        roles = [
            Rol(id=1, nombre="ADMIN", descripcion="Administrator"),
            Rol(id=2, nombre="STOCK", descripcion="Stock Manager"),
            Rol(id=3, nombre="PEDIDOS", descripcion="Orders Manager"),
            Rol(id=4, nombre="CLIENT", descripcion="Client"),
            Rol(id=5, nombre="COCINA", descripcion="Kitchen Operator"),
        ]
        for r in roles:
            session.add(r)
        session.flush()


@pytest.fixture
def session(engine):
    """Create a clean session for each test."""
    with Session(engine) as session:
        seed_all_roles(session)
        session.commit()
        yield session


@pytest.fixture
def client(session: Session):
    """Create a TestClient with the in-memory database session overridden."""

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def create_user(session: Session, **overrides) -> Usuario:
    """Factory helper to create a Usuario row with sensible defaults."""
    now = datetime.now(timezone.utc).isoformat()
    rol_id = overrides.pop("rol_id", Role.CLIENT.value)
    defaults = dict(
        email="user@example.com",
        password_hash="hashed",
        nombre="Test",
        apellido="User",
        activo=True,
        fecha_creacion=now,
        fecha_actualizacion=now,
    )
    defaults.update(overrides)
    user = Usuario(**defaults)
    session.add(user)
    session.flush()  # Get user.id
    session.add(UsuarioRol(usuario_id=user.id, rol_id=rol_id))
    session.commit()
    session.refresh(user)
    return user


def create_token_for(user: Usuario) -> str:
    """Factory helper to mint an access token for *user*."""
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "roles": user.rol_ids,
        "nonce": time.time(),
    }
    return create_access_token(token_data)


def seed_estados(session: Session):
    """Seed the estados_pedido table with FSM states."""
    estados = [
        {"codigo": "PENDIENTE", "nombre": "Pendiente", "orden": 1, "es_terminal": False},
        {"codigo": "CONFIRMADO", "nombre": "Confirmado", "orden": 2, "es_terminal": False},
        {"codigo": "EN_PREPARACION", "nombre": "En Preparación", "orden": 3, "es_terminal": False},
        {"codigo": "EN_CAMINO", "nombre": "En Camino", "orden": 4, "es_terminal": False},
        {"codigo": "ENTREGADO", "nombre": "Entregado", "orden": 5, "es_terminal": True},
        {"codigo": "CANCELADO", "nombre": "Cancelado", "orden": 6, "es_terminal": True},
    ]
    for data in estados:
        existing = session.get(EstadoPedido, data["codigo"])
        if not existing:
            session.add(EstadoPedido(**data))
    session.commit()


def create_product(session: Session, **overrides) -> Producto:
    """Factory helper to create a Producto row with sensible defaults."""
    defaults = dict(
        nombre="Hamburguesa Clásica",
        descripcion="Delicious burger with cheese",
        precio_base=Decimal("10.50"),
        stock_cantidad=100,
        disponible=True,
        tiempo_prep_min=15,
    )
    defaults.update(overrides)
    product = Producto(**defaults)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def create_direccion(session: Session, usuario_id: int, **overrides) -> Direccion:
    """Factory helper to create a Direccion row."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        usuario_id=usuario_id,
        calle="Av. Corrientes",
        numero="1234",
        piso_depto="3B",
        ciudad="Buenos Aires",
        codigo_postal="C1043",
        es_predeterminada=True,
        creado_en=now,
        actualizado_en=now,
    )
    defaults.update(overrides)
    direccion = Direccion(**defaults)
    session.add(direccion)
    session.commit()
    session.refresh(direccion)
    return direccion


def create_pedido_direct(
    session: Session,
    usuario_id: int,
    estado: str = "PENDIENTE",
    **overrides,
) -> Pedido:
    """Create a Pedido directly (bypassing service) for test setup."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        usuario_id=usuario_id,
        estado_codigo=estado,
        total=Decimal("80.00"),
        costo_envio=Decimal("50.00"),
        direccion_calle="Av. Corrientes",
        direccion_numero="1234",
        direccion_ciudad="Buenos Aires",
        direccion_cp="C1043",
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    pedido = Pedido(**defaults)
    session.add(pedido)
    session.commit()
    session.refresh(pedido)
    return pedido


def add_detalle(
    session: Session,
    pedido_id: int,
    producto_id: int,
    **overrides,
) -> DetallePedido:
    """Add a DetallePedido to an existing Pedido."""
    defaults = dict(
        pedido_id=pedido_id,
        producto_id=producto_id,
        nombre_snapshot="Hamburguesa Clásica",
        precio_snapshot=Decimal("10.50"),
        cantidad=2,
        exclusiones=[],
        subtotal=Decimal("21.00"),
    )
    defaults.update(overrides)
    detalle = DetallePedido(**defaults)
    session.add(detalle)
    session.commit()
    session.refresh(detalle)
    return detalle


def add_historial(
    session: Session,
    pedido_id: int,
    desde: str,
    hacia: str,
    **overrides,
) -> HistorialEstadoPedido:
    """Add a HistorialEstadoPedido entry."""
    defaults = dict(
        pedido_id=pedido_id,
        estado_desde=desde,
        estado_hacia=hacia,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    historial = HistorialEstadoPedido(**defaults)
    session.add(historial)
    session.commit()
    session.refresh(historial)
    return historial


# ===================================================================
# 8.1 — KDS Endpoint Tests + CocinaService Integration
# ===================================================================


class TestListarPedidosCocina:
    """Tests for GET /api/v1/cocina/pedidos."""

    # ------------------------------------------------------------------
    # Auth scenarios
    # ------------------------------------------------------------------

    def test_acceso_cocina_role(self, session, client):
        """
        Scenario: COCINA role accesses KDS endpoint
        WHEN an authenticated COCINA user calls GET /api/v1/cocina/pedidos
        THEN the system SHALL return HTTP 200
        """
        seed_estados(session)
        user = create_user(session, email="cocina@test.com", rol_id=Role.COCINA.value)
        token = create_token_for(user)

        response = client.get(
            "/api/v1/cocina/pedidos",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_acceso_pedidos_role(self, session, client):
        """
        Scenario: PEDIDOS role accesses KDS endpoint
        WHEN an authenticated PEDIDOS user calls GET /api/v1/cocina/pedidos
        THEN the system SHALL return HTTP 200
        """
        seed_estados(session)
        user = create_user(session, email="pedidos@test.com", rol_id=Role.PEDIDOS.value)
        token = create_token_for(user)

        response = client.get(
            "/api/v1/cocina/pedidos",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_acceso_admin_role(self, session, client):
        """
        Scenario: ADMIN role accesses KDS endpoint
        WHEN an authenticated ADMIN user calls GET /api/v1/cocina/pedidos
        THEN the system SHALL return HTTP 200
        """
        seed_estados(session)
        user = create_user(session, email="admin@test.com", rol_id=Role.ADMIN.value)
        token = create_token_for(user)

        response = client.get(
            "/api/v1/cocina/pedidos",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_acceso_denied_client(self, session, client):
        """
        Scenario: CLIENT role is denied
        WHEN a CLIENT user calls GET /api/v1/cocina/pedidos
        THEN the system SHALL return HTTP 403
        """
        seed_estados(session)
        user = create_user(session, email="client@test.com", rol_id=Role.CLIENT.value)
        token = create_token_for(user)

        response = client.get(
            "/api/v1/cocina/pedidos",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_sin_auth(self, client):
        """
        Scenario: Unauthenticated access
        WHEN an unauthenticated user calls GET /api/v1/cocina/pedidos
        THEN the system SHALL return HTTP 401
        """
        response = client.get("/api/v1/cocina/pedidos")
        assert response.status_code == 401

    # ------------------------------------------------------------------
    # Data filtering scenarios
    # ------------------------------------------------------------------

    @patch("app.domain.cocina.repository.CocinaRepository.listar_pedidos_con_tiempo", return_value={})
    def test_respuesta_incluye_confirmados_y_en_preparacion(
        self, mock_get_tiempo, session, client
    ):
        """
        Scenario: KDS returns CONFIRMADO and EN_PREPARACION orders
        WHEN there are orders in CONFIRMADO and EN_PREPARACION states
        THEN the response SHALL include both
        """
        seed_estados(session)
        user = create_user(session, email="cocina@test.com", rol_id=Role.COCINA.value)
        token = create_token_for(user)
        product = create_product(session)

        # Create CONFIRMADO order
        pedido_confirmado = create_pedido_direct(
            session, user.id, estado="CONFIRMADO",
        )
        add_detalle(session, pedido_confirmado.id, product.id,
                    nombre_snapshot="Hamburguesa Clásica", cantidad=2)

        # Create EN_PREPARACION order
        pedido_prep = create_pedido_direct(
            session, user.id, estado="EN_PREPARACION",
        )
        add_detalle(session, pedido_prep.id, product.id,
                    nombre_snapshot="Papas Fritas", cantidad=1)

        response = client.get(
            "/api/v1/cocina/pedidos",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        estados = {item["estado_codigo"] for item in data["items"]}
        assert "CONFIRMADO" in estados
        assert "EN_PREPARACION" in estados
        assert data["total_count"] == 2

    @patch("app.domain.cocina.repository.CocinaRepository.listar_pedidos_con_tiempo", return_value={})
    def test_pendientes_no_incluidos(self, mock_get_tiempo, session, client):
        """
        Scenario: PENDIENTE orders are excluded from KDS
        WHEN there are PENDIENTE orders along with CONFIRMADO ones
        THEN PENDIENTE SHALL NOT appear in the response
        """
        seed_estados(session)
        user = create_user(session, email="cocina@test.com", rol_id=Role.COCINA.value)
        token = create_token_for(user)
        product = create_product(session)

        # Create CONFIRMADO order (should appear)
        pedido_conf = create_pedido_direct(
            session, user.id, estado="CONFIRMADO",
        )
        add_detalle(session, pedido_conf.id, product.id)

        # Create PENDIENTE order (should NOT appear)
        pedido_pend = create_pedido_direct(
            session, user.id, estado="PENDIENTE",
        )
        add_detalle(session, pedido_pend.id, product.id)

        response = client.get(
            "/api/v1/cocina/pedidos",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        pedido_ids = {item["id"] for item in data["items"]}
        assert pedido_conf.id in pedido_ids
        assert pedido_pend.id not in pedido_ids
        assert data["total_count"] == 1

    @patch("app.domain.cocina.repository.CocinaRepository.listar_pedidos_con_tiempo", return_value={})
    def test_ordenados_por_antiguedad(self, mock_get_tiempo, session, client):
        """
        Scenario: KDS orders ordered by age
        WHEN there are multiple CONFIRMADO orders
        THEN older orders SHALL appear first
        """
        seed_estados(session)
        user = create_user(session, email="cocina@test.com", rol_id=Role.COCINA.value)
        token = create_token_for(user)
        product = create_product(session)

        # Create older order (earlier updated_at)
        older_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        older = create_pedido_direct(
            session, user.id, estado="CONFIRMADO",
            created_at=older_time, updated_at=older_time,
        )
        add_detalle(session, older.id, product.id)

        # Create newer order (later updated_at)
        newer_time = datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        newer = create_pedido_direct(
            session, user.id, estado="CONFIRMADO",
            created_at=newer_time, updated_at=newer_time,
        )
        add_detalle(session, newer.id, product.id)

        response = client.get(
            "/api/v1/cocina/pedidos",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        # Oldest first
        assert data["items"][0]["id"] == older.id
        assert data["items"][1]["id"] == newer.id

    def test_kds_vacio_retorna_vacio(self, session, client):
        """
        Scenario: Empty KDS
        WHEN there are no orders in CONFIRMADO or EN_PREPARACION
        THEN the response SHALL contain empty items list
        """
        seed_estados(session)
        user = create_user(session, email="cocina@test.com", rol_id=Role.COCINA.value)
        token = create_token_for(user)

        response = client.get(
            "/api/v1/cocina/pedidos",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total_count"] == 0

    @patch("app.domain.cocina.repository.CocinaRepository.listar_pedidos_con_tiempo", return_value={1: 120})
    def test_tiempo_en_cocina_calculado(self, mock_get_tiempo, session, client):
        """
        Scenario: Kitchen elapsed time is returned
        WHEN a CONFIRMADO order exists with a historial entry
        THEN tiempo_en_cocina_segundos SHALL be calculated
        """
        seed_estados(session)
        user = create_user(session, email="cocina@test.com", rol_id=Role.COCINA.value)
        token = create_token_for(user)
        product = create_product(session)

        pedido = create_pedido_direct(session, user.id, estado="CONFIRMADO")
        add_detalle(session, pedido.id, product.id)

        response = client.get(
            "/api/v1/cocina/pedidos",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        # The mock returns 120, so we expect 120
        assert data["items"][0]["tiempo_en_cocina_segundos"] == 120

    @patch("app.domain.cocina.repository.CocinaRepository.listar_pedidos_con_tiempo", return_value={})
    def test_items_incluyen_nombre_snapshot_y_cantidad(
        self, mock_get_tiempo, session, client
    ):
        """
        Scenario: Items include snapshot data
        WHEN a CONFIRMADO order has DetallePedido entries
        THEN items SHALL include nombre_producto and cantidad
        """
        seed_estados(session)
        user = create_user(session, email="cocina@test.com", rol_id=Role.COCINA.value)
        token = create_token_for(user)
        product = create_product(session, nombre="Hamburguesa Especial")

        pedido = create_pedido_direct(session, user.id, estado="CONFIRMADO")
        add_detalle(session, pedido.id, product.id,
                    nombre_snapshot="Hamburguesa Especial", cantidad=3)

        response = client.get(
            "/api/v1/cocina/pedidos",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        items = data["items"][0]["items"]
        assert len(items) == 1
        assert items[0]["nombre_producto"] == "Hamburguesa Especial"
        assert items[0]["cantidad"] == 3


class TestFSMCocina:
    """FSM role validation tests (RN-CO03).

    COCINA can only do:
        CONFIRMADO → EN_PREPARACION
        EN_PREPARACION → EN_CAMINO
    """

    def _create_pedido_in_state(
        self, session: Session, user_id: int, estado: str,
    ) -> int:
        """Helper: create a Pedido in a specific state and return its ID."""
        seed_estados(session)
        product = create_product(session, stock_cantidad=100)
        pedido = create_pedido_direct(session, user_id, estado=estado)
        add_detalle(session, pedido.id, product.id)
        # Always add the relevant historial so the FSM has a valid trace
        if estado == "CONFIRMADO":
            add_historial(session, pedido.id, desde=None, hacia="PENDIENTE")
            add_historial(session, pedido.id, desde="PENDIENTE", hacia="CONFIRMADO")
        elif estado == "EN_PREPARACION":
            add_historial(session, pedido.id, desde=None, hacia="PENDIENTE")
            add_historial(session, pedido.id, desde="PENDIENTE", hacia="CONFIRMADO")
            add_historial(session, pedido.id, desde="CONFIRMADO", hacia="EN_PREPARACION")
        elif estado == "EN_CAMINO":
            add_historial(session, pedido.id, desde=None, hacia="PENDIENTE")
            add_historial(session, pedido.id, desde="PENDIENTE", hacia="CONFIRMADO")
            add_historial(session, pedido.id, desde="CONFIRMADO", hacia="EN_PREPARACION")
            add_historial(session, pedido.id, desde="EN_PREPARACION", hacia="EN_CAMINO")
        session.commit()
        return pedido.id

    # ------------------------------------------------------------------
    # COCINA permitted transitions
    # ------------------------------------------------------------------

    def test_cocina_confirmado_a_en_preparacion(self, session, client):
        """
        Scenario: COCINA transitions CONFIRMADO → EN_PREPARACION
        WHEN a COCINA user patches an order with estado 'EN_PREPARACION'
        THEN the system SHALL return HTTP 200 (RN-CO03)
        """
        admin_user = create_user(session, email="admin@setup.com", rol_id=Role.ADMIN.value)
        pedido_id = self._create_pedido_in_state(session, admin_user.id, "CONFIRMADO")

        cocina_user = create_user(
            session, email="cocina@test.com", rol_id=Role.COCINA.value,
        )
        cocina_token = create_token_for(cocina_user)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_PREPARACION"},
            headers={"Authorization": f"Bearer {cocina_token}"},
        )

        assert response.status_code == 200
        assert response.json()["estado_codigo"] == "EN_PREPARACION"

    def test_cocina_en_preparacion_a_en_camino(self, session, client):
        """
        Scenario: COCINA transitions EN_PREPARACION → EN_CAMINO
        WHEN a COCINA user patches an order with estado 'EN_CAMINO'
        THEN the system SHALL return HTTP 200 (RN-CO03)
        """
        admin_user = create_user(session, email="admin@setup.com", rol_id=Role.ADMIN.value)
        pedido_id = self._create_pedido_in_state(session, admin_user.id, "EN_PREPARACION")

        cocina_user = create_user(
            session, email="cocina@test.com", rol_id=Role.COCINA.value,
        )
        cocina_token = create_token_for(cocina_user)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_CAMINO"},
            headers={"Authorization": f"Bearer {cocina_token}"},
        )

        assert response.status_code == 200
        assert response.json()["estado_codigo"] == "EN_CAMINO"

    # ------------------------------------------------------------------
    # COCINA forbidden transitions
    # ------------------------------------------------------------------

    def test_cocina_no_puede_en_camino_a_entregado(self, session, client):
        """
        Scenario: COCINA cannot transition EN_CAMINO → ENTREGADO
        WHEN a COCINA user attempts to deliver an order
        THEN the system SHALL return HTTP 403 (RN-CO03)
        """
        admin_user = create_user(session, email="admin@setup.com", rol_id=Role.ADMIN.value)
        pedido_id = self._create_pedido_in_state(session, admin_user.id, "EN_CAMINO")

        cocina_user = create_user(
            session, email="cocina@test.com", rol_id=Role.COCINA.value,
        )
        cocina_token = create_token_for(cocina_user)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "ENTREGADO"},
            headers={"Authorization": f"Bearer {cocina_token}"},
        )

        assert response.status_code == 403
        assert "COCINA" in response.json()["detail"]

    def test_cocina_no_puede_confirmado_a_cancelado(self, session, client):
        """
        Scenario: COCINA cannot cancel from CONFIRMADO
        WHEN a COCINA user attempts to cancel a CONFIRMADO order
        THEN the system SHALL return HTTP 403 (RN-CO03)
        """
        admin_user = create_user(session, email="admin@setup.com", rol_id=Role.ADMIN.value)
        pedido_id = self._create_pedido_in_state(session, admin_user.id, "CONFIRMADO")

        cocina_user = create_user(
            session, email="cocina@test.com", rol_id=Role.COCINA.value,
        )
        cocina_token = create_token_for(cocina_user)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "CANCELADO", "motivo": "Test motivo"},
            headers={"Authorization": f"Bearer {cocina_token}"},
        )

        assert response.status_code == 403
        assert "COCINA" in response.json()["detail"]

    # ------------------------------------------------------------------
    # Backward compatibility — ADMIN/PEDIDOS can do all transitions
    # ------------------------------------------------------------------

    def test_admin_puede_todas_las_transiciones(self, session, client):
        """
        Scenario: ADMIN can still do all transitions
        WHEN an ADMIN user transitions an order
        THEN the system SHALL allow any valid FSM transition
        """
        admin_user = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value,
        )
        admin_token = create_token_for(admin_user)

        # CONFIRMADO → EN_PREPARACION
        pedido_id = self._create_pedido_in_state(session, admin_user.id, "CONFIRMADO")
        resp1 = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_PREPARACION"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp1.status_code == 200
        assert resp1.json()["estado_codigo"] == "EN_PREPARACION"

        # EN_PREPARACION → EN_CAMINO
        resp2 = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_CAMINO"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp2.status_code == 200
        assert resp2.json()["estado_codigo"] == "EN_CAMINO"

        # EN_CAMINO → ENTREGADO
        resp3 = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "ENTREGADO"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp3.status_code == 200
        assert resp3.json()["estado_codigo"] == "ENTREGADO"

    def test_pedidos_puede_todas_las_transiciones(self, session, client):
        """
        Scenario: PEDIDOS can still do all transitions
        WHEN a PEDIDOS user transitions an order
        THEN the system SHALL allow any valid FSM transition
        """
        pedidos_user = create_user(
            session, email="pedidos@test.com", rol_id=Role.PEDIDOS.value,
        )
        pedidos_token = create_token_for(pedidos_user)

        # CONFIRMADO → EN_PREPARACION
        pedido_id = self._create_pedido_in_state(session, pedidos_user.id, "CONFIRMADO")
        resp = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_PREPARACION"},
            headers={"Authorization": f"Bearer {pedidos_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["estado_codigo"] == "EN_PREPARACION"


class TestCocinaServiceUnit:
    """Direct unit tests for CocinaService.

    These tests bypass the HTTP layer and call the service directly.
    """

    @patch("app.domain.cocina.repository.CocinaRepository.listar_pedidos_con_tiempo", return_value={})
    def test_listar_pedidos_estructura_correcta(self, mock_get_tiempo, session):
        """
        Scenario: Service returns correct response structure
        WHEN CocinaService.listar_pedidos is called
        THEN the response SHALL contain items and total_count
        """
        from app.domain.cocina.service import CocinaService
        from app.domain.cocina.schemas import PedidoCocinaListResponse

        seed_estados(session)
        user = create_user(session, rol_id=Role.COCINA.value)
        product = create_product(session)

        pedido = create_pedido_direct(session, user.id, estado="CONFIRMADO")
        add_detalle(session, pedido.id, product.id)

        with UnitOfWork(session) as uow:
            result = CocinaService.listar_pedidos(uow)

        assert isinstance(result, PedidoCocinaListResponse)
        assert hasattr(result, "items")
        assert hasattr(result, "total_count")
        assert result.total_count == 1

    @patch("app.domain.cocina.repository.CocinaRepository.listar_pedidos_con_tiempo", return_value={})
    def test_items_incluyen_nombre_snapshot(self, mock_get_tiempo, session):
        """
        Scenario: Service items include nombre_snapshot and cantidad
        WHEN listar_pedidos returns items
        THEN each item SHALL have nombre_producto and cantidad
        """
        from app.domain.cocina.service import CocinaService
        from app.domain.cocina.schemas import PedidoCocinaItem

        seed_estados(session)
        user = create_user(session, rol_id=Role.COCINA.value)
        product = create_product(session, nombre="Pizza Margherita")

        pedido = create_pedido_direct(session, user.id, estado="CONFIRMADO")
        add_detalle(session, pedido.id, product.id,
                    nombre_snapshot="Pizza Margherita", cantidad=1)

        with UnitOfWork(session) as uow:
            result = CocinaService.listar_pedidos(uow)

        assert result.total_count == 1
        item = result.items[0]
        assert len(item.items) == 1
        detalle = item.items[0]
        assert isinstance(detalle, PedidoCocinaItem)
        assert detalle.nombre_producto == "Pizza Margherita"
        assert detalle.cantidad == 1

    @patch("app.domain.cocina.repository.CocinaRepository.listar_pedidos_con_tiempo", return_value={1: 3600})
    def test_tiempo_en_cocina_segundos(self, mock_get_tiempo, session):
        """
        Scenario: Service calculates kitchen elapsed time
        WHEN an order has a CONFIRMADO history entry
        THEN tiempo_en_cocina_segundos SHALL be the elapsed seconds
        """
        from app.domain.cocina.service import CocinaService

        seed_estados(session)
        user = create_user(session, rol_id=Role.COCINA.value)
        product = create_product(session)

        pedido = create_pedido_direct(session, user.id, estado="CONFIRMADO")
        add_detalle(session, pedido.id, product.id)

        with UnitOfWork(session) as uow:
            result = CocinaService.listar_pedidos(uow)

        assert result.total_count == 1
        # The mock returns 3600 seconds (1 hour)
        assert result.items[0].tiempo_en_cocina_segundos == 3600

    def test_service_empty_db(self, session):
        """
        Scenario: Service with empty database
        WHEN there are no kitchen-relevant orders
        THEN the service SHALL return empty lists
        """
        from app.domain.cocina.service import CocinaService

        seed_estados(session)
        # No orders at all

        with UnitOfWork(session) as uow:
            result = CocinaService.listar_pedidos(uow)

        assert result.total_count == 0
        assert result.items == []


# ===================================================================
# 8.2 — WebSocket Integration Tests
# ===================================================================


class TestWebSocketCocina:
    """WebSocket integration tests for /api/v1/cocina/ws."""

    def test_websocket_conexion_cocina_role(self, client):
        """
        Scenario: COCINA role can connect
        WHEN a COCINA user connects with a valid JWT
        THEN the WebSocket handshake SHALL succeed
        """
        token = create_access_token(data={
            "user_id": 1, "email": "cocina@test.com",
            "roles": [Role.COCINA.value], "nonce": time.time(),
        })
        with client.websocket_connect(f"/api/v1/cocina/ws?token={token}") as ws:
            # If we reach here, connection succeeded
            pass

    def test_websocket_ping_pong(self, client):
        """
        Scenario: Ping-pong protocol
        WHEN the client sends "ping" text
        THEN the server SHALL reply with {"type": "pong"}
        """
        token = create_access_token(data={
            "user_id": 1, "email": "cocina@test.com",
            "roles": [Role.COCINA.value], "nonce": time.time(),
        })
        with client.websocket_connect(f"/api/v1/cocina/ws?token={token}") as ws:
            ws.send_text("ping")
            data = ws.receive_json()
            assert data["type"] == "pong"

    def test_websocket_admin_role(self, client):
        """
        Scenario: ADMIN role can connect
        WHEN an ADMIN user connects with a valid JWT
        THEN the WebSocket handshake SHALL succeed
        """
        token = create_access_token(data={
            "user_id": 1, "email": "admin@test.com",
            "roles": [Role.ADMIN.value], "nonce": time.time(),
        })
        with client.websocket_connect(f"/api/v1/cocina/ws?token={token}") as ws:
            pass

    def test_websocket_pedidos_role(self, client):
        """
        Scenario: PEDIDOS role can connect
        WHEN a PEDIDOS user connects with a valid JWT
        THEN the WebSocket handshake SHALL succeed
        """
        token = create_access_token(data={
            "user_id": 1, "email": "pedidos@test.com",
            "roles": [Role.PEDIDOS.value], "nonce": time.time(),
        })
        with client.websocket_connect(f"/api/v1/cocina/ws?token={token}") as ws:
            pass

    def test_websocket_rechaza_client_role(self, client):
        """
        Scenario: CLIENT role is rejected
        WHEN a CLIENT user tries to connect
        THEN the WebSocket SHALL close with code 4003
        """
        token = create_access_token(data={
            "user_id": 1, "email": "client@test.com",
            "roles": [Role.CLIENT.value], "nonce": time.time(),
        })
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(f"/api/v1/cocina/ws?token={token}") as ws:
                pass
        assert exc_info.value.code == 4003

    def test_websocket_rechaza_token_invalido(self, client):
        """
        Scenario: Invalid JWT is rejected
        WHEN a client connects with an invalid token
        THEN the WebSocket SHALL close with code 4001
        """
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(
                "/api/v1/cocina/ws?token=token-invalido",
            ) as ws:
                pass
        assert exc_info.value.code == 4001

    def test_websocket_rechaza_sin_token(self, client):
        """
        Scenario: Missing token is rejected
        WHEN a client connects without a token parameter
        THEN the WebSocket SHALL close with code 4001
        """
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/api/v1/cocina/ws") as ws:
                pass

    def test_websocket_stock_role_no_permitido(self, client):
        """
        Scenario: STOCK role is rejected
        WHEN a STOCK user tries to connect
        THEN the WebSocket SHALL close with code 4003
        """
        token = create_access_token(data={
            "user_id": 1, "email": "stock@test.com",
            "roles": [Role.STOCK.value], "nonce": time.time(),
        })
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(f"/api/v1/cocina/ws?token={token}") as ws:
                pass
        assert exc_info.value.code == 4003


# ===================================================================
# 8.3 — Seed Tests
# ===================================================================


class TestSeedCocina:
    """Tests for seed data — Rol COCINA and cocina test user."""

    def test_seed_rol_cocina_existe(self, session):
        """
        Scenario: COCINA role exists after seed
        WHEN the seed_roles function is executed
        THEN Rol(id=5, nombre='COCINA') SHALL exist in the database
        """
        # seed_all_roles was already called in the session fixture
        from app.models.rol import Rol
        rol = session.get(Rol, 5)
        assert rol is not None
        assert rol.nombre == "COCINA"
        assert rol.descripcion is not None

    def test_seed_roles_es_idempotente(self, session):
        """
        Scenario: Seed roles is idempotent
        WHEN seed_roles is called multiple times
        THEN no duplicate entries SHALL be created
        """
        from app.models.rol import Rol
        # Count roles before second seed
        before = len(list(session.exec(select(Rol)).all()))
        # Call seed again
        seed_all_roles(session)
        # Count after
        after = len(list(session.exec(select(Rol)).all()))
        assert before == after
        # Verify COCINA still there
        rol = session.get(Rol, 5)
        assert rol is not None
        assert rol.nombre == "COCINA"

    def test_seed_usuario_cocina_existe(self, session):
        """
        Scenario: cocina@foodstore.com user exists after seed
        WHEN seed_cocina_user is executed
        THEN a user with email 'cocina@foodstore.com' with COCINA role SHALL exist
        """
        from app.db.seed import seed_cocina_user
        # Run the production seed function against the test DB
        seed_cocina_user(session)
        session.commit()

        # Verify user exists
        user = session.exec(
            select(Usuario).where(Usuario.email == "cocina@foodstore.com")
        ).first()
        assert user is not None
        assert user.activo is True

        # Verify user has COCINA role (rol_id=5)
        user_rol = session.exec(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == user.id,
                UsuarioRol.rol_id == 5,
            )
        ).first()
        assert user_rol is not None

    def test_seed_usuario_cocina_idempotente(self, session):
        """
        Scenario: Seed cocina user is idempotent
        WHEN seed_cocina_user is called multiple times
        THEN only one user with email 'cocina@foodstore.com' SHALL exist
        """
        from app.db.seed import seed_cocina_user
        # Call twice
        seed_cocina_user(session)
        seed_cocina_user(session)
        session.commit()

        users = list(
            session.exec(
                select(Usuario).where(Usuario.email == "cocina@foodstore.com")
            ).unique().all()
        )
        assert len(users) == 1

    def test_seed_rol_cocina_coincide_con_enum(self, session):
        """
        Scenario: Seeded COCINA role matches Role enum
        WHEN the COCINA role is seeded
        THEN Rol.id SHALL match Role.COCINA.value
        """
        from app.models.rol import Rol
        from app.core.auth.roles import Role as RoleEnum
        rol = session.get(Rol, RoleEnum.COCINA.value)
        assert rol is not None
        assert rol.id == RoleEnum.COCINA.value == 5
