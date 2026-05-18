# End-to-end flow test — complete user journey
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


def create_user(session: Session, **overrides) -> Usuario:
    """Factory helper to create a Usuario row."""
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


def create_admin(session: Session) -> Usuario:
    """Factory helper to create an admin user."""
    return create_user(session, email="admin@example.com", rol_id=Role.ADMIN.value)


def create_token_for(user: Usuario) -> str:
    """Mint an access token for *user*."""
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "roles": user.rol_ids,
        "nonce": time.time(),
    }
    return create_access_token(token_data)


def create_product(session: Session, **overrides) -> Producto:
    """Factory helper to create a Producto row."""
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
# E2E Tests
# ===================================================================


class TestE2EFlow:
    """Complete end-to-end user journey: login → order → transition."""

    def test_complete_order_journey(self, session, client):
        """
        Scenario: Complete order life cycle
        GIVEN a registered user with a product and address
        WHEN the user creates an order, views it, and an admin transitions it
        THEN the full flow SHALL work end-to-end
        """
        seed_estados(session)

        # 1. Setup: user, product, address
        user = create_user(session, email="cliente@test.com")
        token = create_token_for(user)
        producto = create_product(session, precio_base=25.0, stock_cantidad=10)
        direccion = create_direccion(session, usuario_id=user.id)

        # 2. Create order
        resp = client.post(
            "/api/v1/pedidos/",
            json={
                "items": [{"producto_id": producto.id, "cantidad": 2, "exclusiones": [1, 3]}],
                "direccion_id": direccion.id,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        pedido = resp.json()
        pedido_id = pedido["id"]
        assert pedido["estado_codigo"] == "PENDIENTE"
        assert pedido["total"] > 0

        # 3. View the order
        resp = client.get(
            f"/api/v1/pedidos/{pedido_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        detail = resp.json()
        assert detail["estado_codigo"] == "PENDIENTE"
        assert len(detail["detalles"]) == 1
        assert detail["detalles"][0]["nombre_snapshot"] == "Hamburguesa Clásica"
        assert detail["detalles"][0]["exclusiones"] == [1, 3]

        # 4. View order history
        resp = client.get(
            f"/api/v1/pedidos/{pedido_id}/historial",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        historial = resp.json()
        assert len(historial) >= 1
        assert historial[0]["estado_desde"] is None
        assert historial[0]["estado_hacia"] == "PENDIENTE"

        # 5. List my orders
        resp = client.get(
            "/api/v1/pedidos/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        lista = resp.json()
        assert lista["total_count"] >= 1
        assert any(p["id"] == pedido_id for p in lista["items"])

        # 6. Admin transitions order
        admin = create_admin(session)
        admin_token = create_token_for(admin)

        # Confirm
        resp = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "CONFIRMADO"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["estado_codigo"] == "CONFIRMADO"

        # To preparation
        resp = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_PREPARACION"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["estado_codigo"] == "EN_PREPARACION"

        # 7. Verify history tracked all transitions
        resp = client.get(
            f"/api/v1/pedidos/{pedido_id}/historial",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        historial = resp.json()
        # Should have: PENDIENTE → CONFIRMADO → EN_PREPARACION (+ initial)
        estados = [h["estado_hacia"] for h in historial]
        assert "PENDIENTE" in estados
        assert "CONFIRMADO" in estados
        assert "EN_PREPARACION" in estados

    def test_auth_required_for_all_endpoints(self, session, client):
        """
        Scenario: Unauthenticated requests are rejected
        WHEN a request is made without a token
        THEN the system SHALL return HTTP 401
        """
        seed_estados(session)

        # Create order without auth
        resp = client.post("/api/v1/pedidos/", json={"items": [], "direccion_id": 1})
        assert resp.status_code == 401

        # List orders without auth
        resp = client.get("/api/v1/pedidos/")
        assert resp.status_code == 401

        # View order without auth
        resp = client.get("/api/v1/pedidos/1")
        assert resp.status_code == 401

        # Profile without auth
        resp = client.get("/api/v1/perfil/")
        assert resp.status_code == 401

        # Metrics without auth
        resp = client.get("/api/v1/admin/metricas/resumen")
        assert resp.status_code == 401

    def test_admin_can_view_all_orders(self, session, client):
        """
        Scenario: Admin can view all orders via admin endpoint
        GIVEN two users with orders
        WHEN an admin lists orders via /admin/pedidos
        THEN ALL orders SHALL be returned
        """
        seed_estados(session)

        # Create two users with orders
        user1 = create_user(session, email="user1@test.com")
        user2 = create_user(session, email="user2@test.com")
        token1 = create_token_for(user1)
        token2 = create_token_for(user2)

        producto = create_product(session, stock_cantidad=20)

        for user, token in [(user1, token1), (user2, token2)]:
            direccion = create_direccion(session, usuario_id=user.id)
            resp = client.post(
                "/api/v1/pedidos/",
                json={
                    "items": [{"producto_id": producto.id, "cantidad": 1, "exclusiones": []}],
                    "direccion_id": direccion.id,
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 201

        # Admin lists all orders
        admin = create_admin(session)
        admin_token = create_token_for(admin)

        resp = client.get(
            "/api/v1/admin/pedidos/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] == 2
