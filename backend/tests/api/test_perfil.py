# Perfil (user profile) endpoints integration tests
import pytest
from datetime import datetime, timezone
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.core.auth.tokens import create_access_token
from app.core.auth.roles import Role
from app.models.usuario import Usuario
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
    defaults = dict(
        email="user@example.com",
        password_hash="hashed",
        nombre="Test",
        apellido="User",
        rol_id=Role.CLIENT.value,
        activo=True,
        fecha_creacion=now,
        fecha_actualizacion=now,
    )
    defaults.update(overrides)
    user = Usuario(**defaults)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_token_for(user: Usuario) -> str:
    """Factory helper to mint an access token for *user*."""
    import time
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "rol_id": user.rol_id,
        "nonce": time.time(),
    }
    return create_access_token(token_data)


# ===================================================================
# Tests
# ===================================================================


class TestGetPerfil:
    """Tests for GET /api/v1/perfil."""

    def test_ver_perfil(self, session, client):
        """
        Scenario: View profile
        WHEN an authenticated user sends GET /api/v1/perfil
        THEN the system SHALL return HTTP 200 with nombre, email, telefono, fecha_creacion
        """
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)

        response = client.get(
            "/api/v1/perfil",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user.email
        assert data["nombre"] == user.nombre
        assert data["apellido"] == user.apellido
        assert "telefono" in data
        assert "fecha_creacion" in data
        assert data["id"] == user.id


class TestUpdatePerfil:
    """Tests for PUT /api/v1/perfil."""

    def test_editar_perfil(self, session, client):
        """
        Scenario: Update profile successfully
        WHEN an authenticated user sends PUT /api/v1/perfil with valid nombre and telefono
        THEN the system SHALL return HTTP 200 with the updated profile
        """
        user = create_user(session, email="edit@test.com", rol_id=Role.CLIENT.value)
        token = create_token_for(user)

        payload = {
            "nombre": "UpdatedName",
            "telefono": "+541112345678",
        }

        response = client.put(
            "/api/v1/perfil",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "UpdatedName"
        assert data["telefono"] == "+541112345678"
        assert data["email"] == "edit@test.com"  # email unchanged

    def test_email_no_se_puede_cambiar(self, session, client):
        """
        Scenario: Email cannot be changed
        WHEN an authenticated user sends PUT /api/v1/perfil with a different email
        THEN the system SHALL ignore the email field and keep the original
        """
        user = create_user(session, email="original@test.com", rol_id=Role.CLIENT.value)
        token = create_token_for(user)

        payload = {
            "email": "hacker@test.com",
            "nombre": "HackerName",
        }

        response = client.put(
            "/api/v1/perfil",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "original@test.com"  # unchanged


class TestChangePassword:
    """Tests for PUT /api/v1/perfil/password."""

    def test_cambiar_password_correctamente(self, session, client):
        """
        Scenario: Change password successfully
        WHEN an authenticated user sends PUT /api/v1/perfil/password
        with correct password_actual and valid password_nueva
        THEN the system SHALL hash and persist the new password
        AND revoke all existing refresh tokens for that user
        AND return HTTP 200
        """
        import bcrypt
        password_hash = bcrypt.hashpw("OldPass123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        user = create_user(session, email="changepwd@test.com", password_hash=password_hash, rol_id=Role.CLIENT.value)
        token = create_token_for(user)

        response = client.put(
            "/api/v1/perfil/password",
            json={
                "password_actual": "OldPass123",
                "password_nueva": "NewSecurePass456",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["detail"] == "Contraseña actualizada correctamente"

        # Verify password was actually changed in DB
        session.refresh(user)
        assert bcrypt.checkpw("NewSecurePass456".encode("utf-8"), user.password_hash.encode("utf-8"))

    def test_password_actual_incorrecta(self, session, client):
        """
        Scenario: Wrong current password
        WHEN an authenticated user sends PUT /api/v1/perfil/password
        with incorrect password_actual
        THEN the system SHALL return HTTP 400 with detail "Contraseña actual incorrecta"
        """
        import bcrypt
        password_hash = bcrypt.hashpw("RealPass123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        user = create_user(session, email="wrongpwd@test.com", password_hash=password_hash, rol_id=Role.CLIENT.value)
        token = create_token_for(user)

        response = client.put(
            "/api/v1/perfil/password",
            json={
                "password_actual": "WrongPass999",
                "password_nueva": "NewSecurePass456",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Contraseña actual incorrecta"

    def test_password_nueva_debil(self, session, client):
        """
        Scenario: Weak new password
        WHEN an authenticated user sends PUT /api/v1/perfil/password
        with password_nueva shorter than 8 characters
        THEN the system SHALL return HTTP 422 with validation error
        """
        import bcrypt
        password_hash = bcrypt.hashpw("OldPass123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        user = create_user(session, email="weakpwd@test.com", password_hash=password_hash, rol_id=Role.CLIENT.value)
        token = create_token_for(user)

        response = client.put(
            "/api/v1/perfil/password",
            json={
                "password_actual": "OldPass123",
                "password_nueva": "1234567",  # 7 chars, should be invalid
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422


class TestAuthRequerido:
    """Tests that all perfil endpoints require authentication."""

    def test_endpoints_requieren_auth(self, session, client):
        """
        Scenario: Endpoints require authentication
        WHEN an unauthenticated user hits any /perfil endpoint
        THEN the system SHALL return HTTP 401
        """
        # GET
        response = client.get("/api/v1/perfil")
        assert response.status_code == 401

        # PUT
        response = client.put(
            "/api/v1/perfil",
            json={"nombre": "Test"},
        )
        assert response.status_code == 401

        # PUT password
        response = client.put(
            "/api/v1/perfil/password",
            json={"password_actual": "x", "password_nueva": "y"},
        )
        assert response.status_code == 401
