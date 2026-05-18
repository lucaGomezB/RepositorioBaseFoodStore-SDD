# Pedidos endpoints integration tests
import pytest
from datetime import datetime, timezone
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import time

from app.main import app
from app.core.auth.tokens import create_access_token
from app.core.auth.roles import Role
from app.models.usuario import Usuario
from app.models.producto import Producto
from app.models.estado_pedido import EstadoPedido
from app.models.direccion import Direccion
from app.core.database import get_db


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


@pytest.fixture
def session(engine):
    """Create a clean session for each test."""
    with Session(engine) as session:
        from tests.conftest import seed_roles
        seed_roles(session)
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
    from app.models.usuario_rol import UsuarioRol
    now = datetime.now(timezone.utc).isoformat()
    # Extract rol_id from overrides (if provided) before passing to Usuario
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
    # Create UsuarioRol pivot entry
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
        descripcion="Deliciosa hamburguesa con queso",
        precio_base=10.50,
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


# ===================================================================
# Tests
# ===================================================================


class TestCrearPedido:
    """Tests for POST /api/v1/pedidos."""

    def test_crear_pedido_exitosamente(self, session, client):
        """
        Scenario: Create order successfully
        WHEN an authenticated CLIENT sends POST /api/v1/pedidos with valid items
        THEN the system SHALL return HTTP 201 with the created order
        """
        seed_estados(session)
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)
        producto = create_product(session, precio_base=15.0, stock_cantidad=10)
        direccion = create_direccion(session, usuario_id=user.id)

        payload = {
            "items": [
                {"producto_id": producto.id, "cantidad": 2, "exclusiones": []},
            ],
            "direccion_id": direccion.id,
        }

        response = client.post(
            "/api/v1/pedidos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["estado_codigo"] == "PENDIENTE"
        assert data["total"] == 80.0  # (15.0 * 2) + 50.0 envio
        assert data["usuario_id"] == user.id
        assert "id" in data
        assert "created_at" in data

    def test_stock_insuficiente_rechaza_pedido(self, session, client):
        """
        Scenario: Insufficient stock rejects order
        WHEN the requested quantity exceeds available stock
        THEN the system SHALL return HTTP 400 Bad Request
        """
        seed_estados(session)
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)
        producto = create_product(session, stock_cantidad=3)
        direccion = create_direccion(session, usuario_id=user.id)

        payload = {
            "items": [
                {"producto_id": producto.id, "cantidad": 10, "exclusiones": []},
            ],
            "direccion_id": direccion.id,
        }

        response = client.post(
            "/api/v1/pedidos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400

    def test_snapshot_precio_y_direccion(self, session, client):
        """
        Scenario: Price and address snapshots
        WHEN an order is created with a product and address
        THEN the order SHALL store the product's price snapshot and address snapshot
        """
        seed_estados(session)
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)
        producto = create_product(session, nombre="Hamburguesa Especial", precio_base=25.0, stock_cantidad=5)
        direccion = create_direccion(
            session,
            usuario_id=user.id,
            calle="Av. Santa Fe",
            numero="567",
            piso_depto="10A",
            ciudad="CABA",
            codigo_postal="C1056",
        )

        payload = {
            "items": [
                {"producto_id": producto.id, "cantidad": 1, "exclusiones": []},
            ],
            "direccion_id": direccion.id,
        }

        response = client.post(
            "/api/v1/pedidos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()

        # Verify snapshot behavior: get detail via GET
        detail_response = client.get(
            f"/api/v1/pedidos/{data['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert detail_response.status_code == 200
        detail = detail_response.json()

        # Price snapshot
        assert len(detail["detalles"]) == 1
        detalle = detail["detalles"][0]
        assert detalle["nombre_snapshot"] == "Hamburguesa Especial"
        assert detalle["precio_snapshot"] == 25.0
        assert detalle["subtotal"] == 25.0

        # Address snapshot
        assert detail["direccion_calle"] == "Av. Santa Fe"
        assert detail["direccion_numero"] == "567"
        assert detail["direccion_piso"] == "10A"
        assert detail["direccion_ciudad"] == "CABA"
        assert detail["direccion_cp"] == "C1056"

    def test_historial_registra_estado_inicial(self, session, client):
        """
        Scenario: Initial history entry
        WHEN an order is created
        THEN the system SHALL create a HistorialEstadoPedido entry
        WITH estado_desde=NULL and estado_hacia='PENDIENTE' (RN-02)
        """
        seed_estados(session)
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)
        producto = create_product(session, precio_base=10.0, stock_cantidad=5)
        direccion = create_direccion(session, usuario_id=user.id)

        payload = {
            "items": [
                {"producto_id": producto.id, "cantidad": 1, "exclusiones": []},
            ],
            "direccion_id": direccion.id,
        }

        response = client.post(
            "/api/v1/pedidos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        pedido_id = response.json()["id"]

        # Get detail to see history
        detail_response = client.get(
            f"/api/v1/pedidos/{pedido_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert detail_response.status_code == 200
        detail = detail_response.json()

        assert len(detail["historial_estados"]) == 1
        historial = detail["historial_estados"][0]
        assert historial["estado_desde"] is None  # RN-02
        assert historial["estado_hacia"] == "PENDIENTE"
        assert "created_at" in historial

    def test_exclusiones_se_almacenan(self, session, client):
        """
        Scenario: Exclusiones stored in DetallePedido
        WHEN an order is created with items that have exclusiones
        THEN the system SHALL store the exclusiones list in the detail
        """
        seed_estados(session)
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)
        producto = create_product(session, precio_base=12.0, stock_cantidad=5)
        direccion = create_direccion(session, usuario_id=user.id)

        payload = {
            "items": [
                {"producto_id": producto.id, "cantidad": 1, "exclusiones": [1, 3, 5]},
            ],
            "direccion_id": direccion.id,
        }

        response = client.post(
            "/api/v1/pedidos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        pedido_id = response.json()["id"]

        # Get detail to see exclusiones
        detail_response = client.get(
            f"/api/v1/pedidos/{pedido_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert detail_response.status_code == 200
        detail = detail_response.json()

        assert len(detail["detalles"]) == 1
        detalle = detail["detalles"][0]
        assert detalle["exclusiones"] == [1, 3, 5]


class TestObtenerPedido:
    """Tests for GET /api/v1/pedidos/{id}."""

    def test_obtener_pedido_propio(self, session, client):
        """
        Scenario: Get own order
        WHEN a CLIENT requests their own order
        THEN the system SHALL return HTTP 200 with order details
        """
        seed_estados(session)
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)
        producto = create_product(session, precio_base=20.0, stock_cantidad=3)
        direccion = create_direccion(session, usuario_id=user.id)

        # Create order first
        payload = {
            "items": [{"producto_id": producto.id, "cantidad": 1, "exclusiones": []}],
            "direccion_id": direccion.id,
        }
        post_resp = client.post(
            "/api/v1/pedidos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert post_resp.status_code == 201
        pedido_id = post_resp.json()["id"]

        # Get it
        response = client.get(
            f"/api/v1/pedidos/{pedido_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pedido_id
        assert "detalles" in data
        assert "historial_estados" in data

    def test_no_puede_ver_pedido_de_otro(self, session, client):
        """
        Scenario: Cannot view another user's order
        WHEN a CLIENT requests another user's order
        THEN the system SHALL return HTTP 404
        """
        seed_estados(session)
        user1 = create_user(session, email="user1@test.com", rol_id=Role.CLIENT.value)
        user2 = create_user(session, email="user2@test.com", rol_id=Role.CLIENT.value)
        token2 = create_token_for(user2)

        producto = create_product(session, stock_cantidad=5)
        direccion = create_direccion(session, usuario_id=user1.id)

        # User1 creates an order
        payload = {
            "items": [{"producto_id": producto.id, "cantidad": 1, "exclusiones": []}],
            "direccion_id": direccion.id,
        }
        token1 = create_token_for(user1)
        post_resp = client.post(
            "/api/v1/pedidos/",
            json=payload,
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert post_resp.status_code == 201
        pedido_id = post_resp.json()["id"]

        # User2 tries to see it
        response = client.get(
            f"/api/v1/pedidos/{pedido_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 404

    def test_sin_auth(self, client):
        """GET /pedidos without token returns 401."""
        response = client.get("/api/v1/pedidos/1")
        assert response.status_code == 401


class TestHistorialPedido:
    """Tests for GET /api/v1/pedidos/{id}/historial."""

    def test_ver_historial_propio(self, session, client):
        """
        Scenario: View own order history
        WHEN a CLIENT requests the history of their own order
        THEN the system SHALL return HTTP 200 with the audit trail
        """
        seed_estados(session)
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)
        producto = create_product(session, precio_base=15.0, stock_cantidad=10)
        direccion = create_direccion(session, usuario_id=user.id)

        # Create order first
        payload = {
            "items": [{"producto_id": producto.id, "cantidad": 1, "exclusiones": []}],
            "direccion_id": direccion.id,
        }
        post_resp = client.post(
            "/api/v1/pedidos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert post_resp.status_code == 201
        pedido_id = post_resp.json()["id"]

        # Get history
        response = client.get(
            f"/api/v1/pedidos/{pedido_id}/historial",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Initial entry: estado_desde None -> estado_hacia PENDIENTE
        first_entry = data[0]
        assert first_entry["estado_desde"] is None
        assert first_entry["estado_hacia"] == "PENDIENTE"
        assert "created_at" in first_entry

    def test_no_ver_historial_ajeno(self, session, client):
        """
        Scenario: Cannot view another user's order history
        WHEN a CLIENT requests the history of another user's order
        THEN the system SHALL return HTTP 404
        """
        seed_estados(session)
        user1 = create_user(session, email="user1@test.com", rol_id=Role.CLIENT.value)
        user2 = create_user(session, email="user2@test.com", rol_id=Role.CLIENT.value)
        token2 = create_token_for(user2)

        producto = create_product(session, stock_cantidad=5)
        direccion = create_direccion(session, usuario_id=user1.id)

        # User1 creates an order
        payload = {
            "items": [{"producto_id": producto.id, "cantidad": 1, "exclusiones": []}],
            "direccion_id": direccion.id,
        }
        token1 = create_token_for(user1)
        post_resp = client.post(
            "/api/v1/pedidos/",
            json=payload,
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert post_resp.status_code == 201
        pedido_id = post_resp.json()["id"]

        # User2 tries to see history
        response = client.get(
            f"/api/v1/pedidos/{pedido_id}/historial",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 404


class TestFSM:
    """Tests for the FSM transition validation."""

    def test_validar_transicion_permitida(self):
        """Valid transitions should return True."""
        from app.domain.pedidos.service import validar_transicion
        assert validar_transicion("PENDIENTE", "CONFIRMADO") is True
        assert validar_transicion("PENDIENTE", "CANCELADO") is True
        assert validar_transicion("CONFIRMADO", "EN_PREPARACION") is True
        assert validar_transicion("EN_PREPARACION", "EN_CAMINO") is True
        assert validar_transicion("EN_CAMINO", "ENTREGADO") is True

    def test_validar_transicion_denegada(self):
        """Invalid transitions should return False."""
        from app.domain.pedidos.service import validar_transicion
        assert validar_transicion("PENDIENTE", "ENTREGADO") is False
        assert validar_transicion("CONFIRMADO", "ENTREGADO") is False
        assert validar_transicion("ENTREGADO", "CANCELADO") is False
        assert validar_transicion("CANCELADO", "PENDIENTE") is False
        assert validar_transicion("ENTREGADO", "EN_CAMINO") is False

    def test_estados_terminales_no_admiten_transiciones(self):
        """Terminal states should have no outgoing transitions."""
        from app.domain.pedidos.service import TRANSICIONES
        assert TRANSICIONES["ENTREGADO"] == []
        assert TRANSICIONES["CANCELADO"] == []


class TestTransicionEstado:
    """Tests for PATCH /api/v1/pedidos/{id}/estado."""

    def _crear_pedido(self, session, client, token, user_id) -> int:
        """Helper: create an order and return its ID."""
        seed_estados(session)
        producto = create_product(session, precio_base=15.0, stock_cantidad=10)
        direccion = create_direccion(session, usuario_id=user_id)

        payload = {
            "items": [{"producto_id": producto.id, "cantidad": 2, "exclusiones": []}],
            "direccion_id": direccion.id,
        }
        resp = client.post(
            "/api/v1/pedidos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        return resp.json()["id"], producto

    def _transicionar(self, client, token, pedido_id, nuevo_estado, motivo=None):
        """Helper: call PATCH /pedidos/{id}/estado and return response."""
        body = {"nuevo_estado": nuevo_estado}
        if motivo is not None:
            body["motivo"] = motivo
        return client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        )

    # ------------------------------------------------------------------
    # 4.1  PENDIENTE -> CANCELADO
    # ------------------------------------------------------------------

    def test_pendiente_a_cancelado(self, session, client):
        """
        Scenario: Cancel a pending order
        WHEN an ADMIN transitions a PENDIENTE order to CANCELADO
        THEN the system SHALL return HTTP 200 with estado_codigo='CANCELADO'
        """
        user = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(user)
        pedido_id, _ = self._crear_pedido(session, client, token, user.id)

        resp = self._transicionar(
            client, token, pedido_id, "CANCELADO", motivo="Cliente solicita cancelacion",
        )
        assert resp.status_code == 200
        assert resp.json()["estado_codigo"] == "CANCELADO"

        # Verify history entry
        detail = client.get(
            f"/api/v1/pedidos/{pedido_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert detail.status_code == 200
        historiales = detail.json()["historial_estados"]
        last_entry = historiales[-1]
        assert last_entry["estado_desde"] == "PENDIENTE"
        assert last_entry["estado_hacia"] == "CANCELADO"
        assert last_entry["motivo"] == "Cliente solicita cancelacion"

    # ------------------------------------------------------------------
    # 4.2  CONFIRMADO -> CANCELADO con restauro stock
    # ------------------------------------------------------------------

    def test_confirmado_a_cancelado_restaura_stock(self, session, client):
        """
        Scenario: Cancel a confirmed order restores stock
        WHEN an ADMIN transitions a CONFIRMADO order to CANCELADO
        THEN the system SHALL restore the product stock AND return HTTP 200
        """
        user = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(user)
        pedido_id, producto = self._crear_pedido(session, client, token, user.id)

        # Confirm the order
        resp = self._transicionar(client, token, pedido_id, "CONFIRMADO")
        assert resp.status_code == 200

        # Verify stock was decremented
        session.refresh(producto)

        # Cancel with motivo
        resp = self._transicionar(
            client, token, pedido_id, "CANCELADO", motivo="Sin stock de insumos",
        )
        assert resp.status_code == 200
        assert resp.json()["estado_codigo"] == "CANCELADO"

        # Verify stock was restored
        session.refresh(producto)
        assert producto.stock_cantidad == 10  # Back to original

    # ------------------------------------------------------------------
    # 4.3  CONFIRMADO -> EN_PREPARACION
    # ------------------------------------------------------------------

    def test_confirmado_a_en_preparacion(self, session, client):
        """
        Scenario: Transition from CONFIRMADO to EN_PREPARACION
        WHEN an ADMIN transitions a CONFIRMADO order to EN_PREPARACION
        THEN the system SHALL return HTTP 200 with estado_codigo='EN_PREPARACION'
        """
        user = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(user)
        pedido_id, _ = self._crear_pedido(session, client, token, user.id)

        # Confirm first
        resp = self._transicionar(client, token, pedido_id, "CONFIRMADO")
        assert resp.status_code == 200

        # Transition to EN_PREPARACION
        resp = self._transicionar(client, token, pedido_id, "EN_PREPARACION")
        assert resp.status_code == 200
        assert resp.json()["estado_codigo"] == "EN_PREPARACION"

    # ------------------------------------------------------------------
    # 4.4  Transición inválida rechazada
    # ------------------------------------------------------------------

    def test_transicion_invalida_rechazada(self, session, client):
        """
        Scenario: Invalid transition is rejected
        WHEN an ADMIN attempts an invalid transition (e.g. PENDIENTE -> ENTREGADO)
        THEN the system SHALL return HTTP 400
        """
        user = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(user)
        pedido_id, _ = self._crear_pedido(session, client, token, user.id)

        resp = self._transicionar(client, token, pedido_id, "ENTREGADO")
        assert resp.status_code == 400
        assert "no permitida" in resp.text.lower()

    # ------------------------------------------------------------------
    # 4.5  Cancelación sin motivo rechazada
    # ------------------------------------------------------------------

    def test_cancelacion_sin_motivo_rechazada(self, session, client):
        """
        Scenario: Cancellation without motivo is rejected
        WHEN an ADMIN attempts to cancel an order without providing a motivo
        THEN the system SHALL return HTTP 400
        """
        user = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(user)
        pedido_id, _ = self._crear_pedido(session, client, token, user.id)

        resp = self._transicionar(client, token, pedido_id, "CANCELADO")
        assert resp.status_code == 400
        assert "motivo" in resp.text.lower()

    # ------------------------------------------------------------------
    # 4.6  Historial registra usuario
    # ------------------------------------------------------------------

    def test_historial_registra_usuario(self, session, client):
        """
        Scenario: History records which user performed the transition
        WHEN an ADMIN transitions an order
        THEN the HistorialEstadoPedido entry SHALL include usuario_id
        """
        user = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(user)
        pedido_id, _ = self._crear_pedido(session, client, token, user.id)

        # Confirm then transition to EN_PREPARACION
        self._transicionar(client, token, pedido_id, "CONFIRMADO")
        resp = self._transicionar(client, token, pedido_id, "EN_PREPARACION")
        assert resp.status_code == 200

        # Verify history entry has usuario_id via direct DB query
        from app.models.historial_estado_pedido import HistorialEstadoPedido
        from sqlmodel import select
        stmt = (
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.id.desc())
        )
        entry = session.exec(stmt).first()
        assert entry is not None
        # The latest entry should be EN_PREPARACION, from CONFIRMADO
        assert entry.estado_hacia == "EN_PREPARACION"
        assert entry.usuario_id == user.id  # usuario_id set by transicionar_estado

    # ------------------------------------------------------------------
    # 4.7  Roles: CLIENT no puede transicionar
    # ------------------------------------------------------------------

    def test_cliente_no_puede_transicionar(self, session, client):
        """
        Scenario: CLIENT role cannot transition orders
        WHEN a CLIENT attempts to patch /pedidos/{id}/estado
        THEN the system SHALL return HTTP 403
        """
        # Create order as ADMIN
        admin_user = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value,
        )
        admin_token = create_token_for(admin_user)
        pedido_id, _ = self._crear_pedido(session, client, admin_token, admin_user.id)

        # Try to transition as CLIENT
        client_user = create_user(
            session, email="client@test.com", rol_id=Role.CLIENT.value,
        )
        client_token = create_token_for(client_user)

        resp = self._transicionar(client, client_token, pedido_id, "CONFIRMADO")
        assert resp.status_code == 403
