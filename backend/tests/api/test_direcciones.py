# Direcciones endpoints integration tests
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


def create_direccion_in_db(
    session: Session,
    usuario_id: int,
    **overrides,
) -> Direccion:
    """Create a Direccion directly in the DB (bypassing API)."""
    from datetime import datetime
    now = datetime.now(timezone.utc)
    defaults = dict(
        usuario_id=usuario_id,
        calle="Av. Siempre Viva",
        numero="742",
        piso_depto=None,
        ciudad="Springfield",
        codigo_postal="1234",
        es_predeterminada=False,
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


class TestCrearDireccion:
    """Tests for POST /api/v1/direcciones."""

    def test_crear_direccion_como_client(self, session, client):
        """
        Scenario: Create address successfully
        WHEN an authenticated CLIENT sends POST /api/v1/direcciones with valid fields
        THEN the system SHALL return HTTP 201 with the created address
        """
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)

        payload = {
            "calle": "Av. Corrientes",
            "numero": "1234",
            "piso_depto": "3B",
            "ciudad": "Buenos Aires",
            "codigo_postal": "C1043",
        }

        response = client.post(
            "/api/v1/direcciones/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["calle"] == "Av. Corrientes"
        assert data["numero"] == "1234"
        assert data["piso_depto"] == "3B"
        assert data["ciudad"] == "Buenos Aires"
        assert data["codigo_postal"] == "C1043"
        assert data["usuario_id"] == user.id
        assert "id" in data
        assert "creado_en" in data
        assert "actualizado_en" in data

    def test_primera_direccion_se_marca_predeterminada(self, session, client):
        """
        Scenario: First address is auto-marked as default
        AND if this is the user's first address, es_predeterminada SHALL be true
        """
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)

        payload = {
            "calle": "Av. Santa Fe",
            "numero": "567",
            "ciudad": "Buenos Aires",
            "codigo_postal": "C1056",
        }

        response = client.post(
            "/api/v1/direcciones/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["es_predeterminada"] is True

    def test_crear_direccion_sin_auth(self, client):
        """
        Scenario: Create address without auth
        WHEN an unauthenticated user sends POST /api/v1/direcciones
        THEN the system SHALL return HTTP 401 Unauthorized
        """
        payload = {
            "calle": "Av. Siempre Viva",
            "numero": "742",
            "ciudad": "Springfield",
            "codigo_postal": "1234",
        }

        response = client.post(
            "/api/v1/direcciones/",
            json=payload,
        )

        assert response.status_code == 401


class TestListarDirecciones:
    """Tests for GET /api/v1/direcciones."""

    def test_listar_solo_muestra_direcciones_del_usuario(self, session, client):
        """
        Scenario: List own addresses
        WHEN an authenticated CLIENT sends GET /api/v1/direcciones
        THEN the system SHALL return HTTP 200 with only that user's addresses
        """
        user1 = create_user(session, email="user1@test.com", rol_id=Role.CLIENT.value)
        user2 = create_user(session, email="user2@test.com", rol_id=Role.CLIENT.value)
        token1 = create_token_for(user1)

        # Create addresses for user1
        create_direccion_in_db(session, usuario_id=user1.id, calle="Calle 1")
        create_direccion_in_db(session, usuario_id=user1.id, calle="Calle 2")

        # Create address for user2 (should NOT appear)
        create_direccion_in_db(session, usuario_id=user2.id, calle="Calle Otro")

        response = client.get(
            "/api/v1/direcciones/",
            headers={"Authorization": f"Bearer {token1}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        calles = [d["calle"] for d in data]
        assert "Calle 1" in calles
        assert "Calle 2" in calles
        assert "Calle Otro" not in calles

    def test_listar_sin_auth(self, client):
        """GET /direcciones without token returns 401."""
        response = client.get("/api/v1/direcciones/")
        assert response.status_code == 401


class TestOwnershipValidation:
    """Tests that users cannot access other users' addresses (returns 404)."""

    def test_no_se_puede_ver_editar_eliminar_direccion_de_otro_usuario(self, session, client):
        """
        Scenario: Update another user's address
        WHEN an authenticated user sends PUT /api/v1/direcciones/{id} for an address owned by another user
        THEN the system SHALL return HTTP 404 Not Found

        Also tests GET by ID returns 404, and DELETE returns 404 for other user's address.
        """
        user1 = create_user(session, email="user1@test.com", rol_id=Role.CLIENT.value)
        user2 = create_user(session, email="user2@test.com", rol_id=Role.CLIENT.value)
        token2 = create_token_for(user2)

        # Create address for user1
        direccion = create_direccion_in_db(session, usuario_id=user1.id)

        # Try GET (there's no GET by ID endpoint, but PUT and DELETE should return 404)
        # Try UPDATE
        response = client.put(
            f"/api/v1/direcciones/{direccion.id}",
            json={"calle": "Calle Hackeada"},
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 404

        # Try DELETE
        response = client.delete(
            f"/api/v1/direcciones/{direccion.id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 404

    def test_delete_nonexistent_address(self, session, client):
        """
        Scenario: Delete nonexistent address
        WHEN an authenticated user sends DELETE /api/v1/direcciones/99999
        THEN the system SHALL return HTTP 404 Not Found
        """
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)

        response = client.delete(
            "/api/v1/direcciones/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404


class TestMarcarPredeterminada:
    """Tests for PATCH /api/v1/direcciones/{id}/predeterminada."""

    def test_marcar_predeterminada_desmarca_anterior(self, session, client):
        """
        Scenario: Set address as default
        WHEN an authenticated user sends PATCH /api/v1/direcciones/{id}/predeterminada
        THEN the system SHALL set that address as es_predeterminada=true
        AND all other addresses for that user SHALL have es_predeterminada=false
        """
        user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(user)

        # Create first address (auto-default)
        dir1 = create_direccion_in_db(session, usuario_id=user.id, calle="Default Antigua", es_predeterminada=True)
        # Create second address (not default)
        dir2 = create_direccion_in_db(session, usuario_id=user.id, calle="Nueva Default", es_predeterminada=False)

        response = client.patch(
            f"/api/v1/direcciones/{dir2.id}/predeterminada",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["es_predeterminada"] is True
        assert data["id"] == dir2.id

        # Verify the old default is no longer default
        session.expire_all()
        old_default = session.get(Direccion, dir1.id)
        assert old_default is not None
        assert old_default.es_predeterminada is False

    def test_marcar_predeterminada_sin_auth(self, session, client):
        """PATCH /direcciones/{id}/predeterminada without token returns 401."""
        user = create_user(session, rol_id=Role.CLIENT.value)
        direccion = create_direccion_in_db(session, usuario_id=user.id)

        response = client.patch(
            f"/api/v1/direcciones/{direccion.id}/predeterminada",
        )
        assert response.status_code == 401


class TestAuthRequerido:
    """Tests that all endpoints require authentication."""

    def test_todos_los_endpoints_requieren_auth(self, session, client):
        """
        Scenario: Endpoints require authentication
        WHEN an unauthenticated user hits any /direcciones endpoint
        THEN the system SHALL return HTTP 401
        """
        user = create_user(session, rol_id=Role.CLIENT.value)
        # Create an address to have a valid ID
        direccion = create_direccion_in_db(session, usuario_id=user.id)

        # POST
        response = client.post(
            "/api/v1/direcciones/",
            json={"calle": "Test", "numero": "123", "ciudad": "City", "codigo_postal": "1234"},
        )
        assert response.status_code == 401

        # GET
        response = client.get("/api/v1/direcciones/")
        assert response.status_code == 401

        # PUT
        response = client.put(
            f"/api/v1/direcciones/{direccion.id}",
            json={"calle": "Test"},
        )
        assert response.status_code == 401

        # DELETE
        response = client.delete(f"/api/v1/direcciones/{direccion.id}")
        assert response.status_code == 401

        # PATCH
        response = client.patch(f"/api/v1/direcciones/{direccion.id}/predeterminada")
        assert response.status_code == 401
