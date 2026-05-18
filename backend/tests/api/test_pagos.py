# Pagos endpoints integration tests
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import time

from app.main import app
from app.core.auth.tokens import create_access_token
from app.core.auth.roles import Role
from app.models.usuario import Usuario
from app.models.pedido import Pedido
from app.models.estado_pedido import EstadoPedido
from app.core.database import get_db
from app.core.config import settings


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_webhook_secret():
    """Clear webhook secret for tests to skip signature validation."""
    original = settings.MERCADOPAGO_WEBHOOK_SECRET
    settings.MERCADOPAGO_WEBHOOK_SECRET = ""
    yield
    settings.MERCADOPAGO_WEBHOOK_SECRET = original


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
    ]
    for data in estados:
        session.add(EstadoPedido(**data))
    session.commit()


def create_pedido(session: Session, usuario_id: int, estado: str = "PENDIENTE") -> Pedido:
    """Factory helper to create a Pedido row."""
    now = datetime.now(timezone.utc)
    pedido = Pedido(
        usuario_id=usuario_id,
        estado_codigo=estado,
        total=150.00,
        costo_envio=50.00,
        direccion_calle="Av. Siempre Viva",
        direccion_numero="123",
        direccion_ciudad="Springfield",
        direccion_cp="1234",
        created_at=now,
        updated_at=now,
    )
    session.add(pedido)
    session.commit()
    session.refresh(pedido)
    return pedido


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCrearPago:
    """Tests for POST /api/v1/pagos/crear"""

    @patch("app.domain.pagos.service.PagoService._get_sdk")
    def test_crear_pago_exitoso(self, mock_get_sdk, client, session):
        """7.1 Creación exitosa de pago."""
        seed_estados(session)
        user = create_user(session)
        token = create_token_for(user)
        pedido = create_pedido(session, user.id)

        # Mock MP SDK to return a successful preference
        mock_sdk = MagicMock()
        mock_preference = MagicMock()
        mock_preference.create.return_value = {
            "response": {
                "id": "pref_test_123",
                "status": "approved",
                "status_detail": "accredited",
                "init_point": "https://mercadopago.com/checkout/test",
            }
        }
        mock_sdk.preference.return_value = mock_preference
        mock_get_sdk.return_value = mock_sdk

        response = client.post(
            "/api/v1/pagos/crear",
            json={"pedido_id": pedido.id},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["pedido_id"] == pedido.id
        assert data["mp_status"] == "approved"
        assert data["external_reference"].startswith(str(pedido.id))

    def test_crear_pago_pedido_no_encontrado(self, client, session):
        """7.2 Creación de pago con pedido inexistente (404)."""
        user = create_user(session)
        token = create_token_for(user)

        response = client.post(
            "/api/v1/pagos/crear",
            json={"pedido_id": 9999},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()

    def test_crear_pago_pedido_no_pendiente(self, client, session):
        """7.3 Creación de pago con pedido no en PENDIENTE (409)."""
        seed_estados(session)
        user = create_user(session)
        token = create_token_for(user)
        # Create order with CONFIRMADO state (not PENDIENTE)
        pedido = create_pedido(session, user.id, estado="CONFIRMADO")

        response = client.post(
            "/api/v1/pagos/crear",
            json={"pedido_id": pedido.id},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409
        assert "PENDIENTE" in response.json()["detail"]

    @patch("app.domain.pagos.service.PagoService._get_sdk")
    def test_crear_pago_idempotencia(self, mock_get_sdk, client, session):
        """7.4 Idempotencia: mismo pedido con diferentes idempotency_key crea pagos diferentes."""
        seed_estados(session)
        user = create_user(session)
        token = create_token_for(user)
        pedido = create_pedido(session, user.id)

        # Use a counter to return different mp_payment_id per call
        call_count = [0]

        def preference_create_side_effect(*args, **kwargs):
            call_count[0] += 1
            return {
                "response": {
                    "id": f"pref_{call_count[0]}",
                    "status": "pending",
                    "status_detail": "pending",
                    "init_point": "https://mercadopago.com/checkout/test",
                }
            }

        mock_sdk = MagicMock()
        mock_preference = MagicMock()
        mock_preference.create.side_effect = preference_create_side_effect
        mock_sdk.preference.return_value = mock_preference
        mock_get_sdk.return_value = mock_sdk

        # First call — should create
        resp1 = client.post(
            "/api/v1/pagos/crear",
            json={"pedido_id": pedido.id},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp1.status_code == 201

        # Second call — should create a different payment (different idempotency_key)
        resp2 = client.post(
            "/api/v1/pagos/crear",
            json={"pedido_id": pedido.id},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp2.status_code == 201
        # Should have different IDs
        assert resp2.json()["id"] != resp1.json()["id"]


class TestObtenerPago:
    """Tests for GET /api/v1/pagos/{pedido_id}"""

    @patch("app.domain.pagos.service.PagoService._get_sdk")
    def test_obtener_pago_por_pedido(self, mock_get_sdk, client, session):
        """7.5 Consulta de pago por pedido_id."""
        seed_estados(session)
        user = create_user(session)
        token = create_token_for(user)
        pedido = create_pedido(session, user.id)

        # Create a payment first
        mock_sdk = MagicMock()
        mock_preference = MagicMock()
        mock_preference.create.return_value = {
            "response": {
                "id": "pref_789",
                "status": "approved",
                "status_detail": "accredited",
                "init_point": "https://mercadopago.com/checkout/test",
            }
        }
        mock_sdk.preference.return_value = mock_preference
        mock_get_sdk.return_value = mock_sdk

        client.post(
            "/api/v1/pagos/crear",
            json={"pedido_id": pedido.id},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Now query the payment
        response = client.get(
            f"/api/v1/pagos/{pedido.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pedido_id"] == pedido.id
        assert data["mp_status"] == "approved"

    def test_obtener_pago_ownership(self, client, session):
        """7.9 Ownership: cliente no puede ver pago de otro usuario."""
        seed_estados(session)
        owner = create_user(session, email="owner@test.com")
        other = create_user(session, email="other@test.com")
        other_token = create_token_for(other)

        pedido = create_pedido(session, owner.id)
        pedido.usuario_id = owner.id
        session.commit()

        response = client.get(
            f"/api/v1/pagos/{pedido.id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )

        # Should be 404 (not revealing ownership)
        assert response.status_code == 404


class TestWebhookPago:
    """Tests for POST /api/v1/pagos/webhook"""

    @patch("app.domain.pagos.service.PagoService._get_sdk")
    def test_webhook_pago_aprobado(self, mock_get_sdk, client, session):
        """7.6 Webhook con pago aprobado → transición a CONFIRMADO."""
        seed_estados(session)
        user = create_user(session)
        pedido = create_pedido(session, user.id)

        # First, register the payment
        mock_sdk = MagicMock()
        mock_payment = MagicMock()

        # Mock the payment.get() call for webhook verification
        mock_payment.get.return_value = {
            "response": {
                "id": 12345,
                "status": "approved",
                "status_detail": "accredited",
                "external_reference": f"{pedido.id}-testabc",
            }
        }
        mock_sdk.payment.return_value = mock_payment
        mock_get_sdk.return_value = mock_sdk

        # Simulate MP webhook call
        response = client.post(
            "/api/v1/pagos/webhook",
            json={
                "type": "payment",
                "data": {"id": "12345"},
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "processed"

        # Verify that the order was transitioned to CONFIRMADO
        session.refresh(pedido)
        assert pedido.estado_codigo == "CONFIRMADO"

    @patch("app.domain.pagos.service.PagoService._get_sdk")
    def test_webhook_pago_rechazado(self, mock_get_sdk, client, session):
        """7.7 Webhook con pago rechazado → pedido sigue PENDIENTE."""
        seed_estados(session)
        user = create_user(session)
        pedido = create_pedido(session, user.id)

        mock_sdk = MagicMock()
        mock_payment = MagicMock()
        mock_payment.get.return_value = {
            "response": {
                "id": 54321,
                "status": "rejected",
                "status_detail": "cc_rejected_other_reason",
                "external_reference": f"{pedido.id}-testxyz",
            }
        }
        mock_sdk.payment.return_value = mock_payment
        mock_get_sdk.return_value = mock_sdk

        response = client.post(
            "/api/v1/pagos/webhook",
            json={
                "type": "payment",
                "data": {"id": "54321"},
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "processed"

        # Verify order is still PENDIENTE
        session.refresh(pedido)
        assert pedido.estado_codigo == "PENDIENTE"

    @patch("app.domain.pagos.service.PagoService._get_sdk")
    def test_webhook_duplicado(self, mock_get_sdk, client, session):
        """7.8 Webhook duplicado (mismo mp_payment_id y mismo estado)."""
        seed_estados(session)
        user = create_user(session)
        pedido = create_pedido(session, user.id)

        mock_sdk = MagicMock()
        mock_payment = MagicMock()
        mock_payment.get.return_value = {
            "response": {
                "id": 99999,
                "status": "approved",
                "status_detail": "accredited",
                "external_reference": f"{pedido.id}-testdup",
            }
        }
        mock_sdk.payment.return_value = mock_payment
        mock_get_sdk.return_value = mock_sdk

        # First webhook
        resp1 = client.post(
            "/api/v1/pagos/webhook",
            json={
                "type": "payment",
                "data": {"id": "99999"},
            },
        )
        assert resp1.json()["status"] == "processed"

        # Second webhook with same data
        resp2 = client.post(
            "/api/v1/pagos/webhook",
            json={
                "type": "payment",
                "data": {"id": "99999"},
            },
        )
        result2 = resp2.json()
        assert result2["status"] == "duplicate"

        # Order should only be CONFIRMADO once
        session.refresh(pedido)
        assert pedido.estado_codigo == "CONFIRMADO"

    def test_webhook_firma_invalida(self, client, session):
        """7.10 Webhook con firma inválida → 403."""
        # Set webhook secret so validation runs
        settings.MERCADOPAGO_WEBHOOK_SECRET = "test_secret"

        response = client.post(
            "/api/v1/pagos/webhook",
            json={
                "type": "payment",
                "data": {"id": "12345"},
            },
        )

        assert response.status_code == 403
        assert "firma" in response.json()["detail"].lower()

        # Reset
        settings.MERCADOPAGO_WEBHOOK_SECRET = ""

    def test_webhook_sin_firma(self, client, session):
        """7.11 Webhook sin header X-Signature → 403 (cuando hay secret configurado)."""
        settings.MERCADOPAGO_WEBHOOK_SECRET = "test_secret"

        response = client.post(
            "/api/v1/pagos/webhook",
            json={
                "type": "payment",
                "data": {"id": "12345"},
            },
            headers={},
        )

        assert response.status_code == 403

        # Reset
        settings.MERCADOPAGO_WEBHOOK_SECRET = ""
