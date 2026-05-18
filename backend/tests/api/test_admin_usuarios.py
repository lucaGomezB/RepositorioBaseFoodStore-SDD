"""Tests for /admin/usuarios CRUD endpoints."""
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
# Fixtures – in-memory SQLite
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


def auth_header(user: Usuario) -> dict:
    """Return Authorization header dict for *user*."""
    return {"Authorization": f"Bearer {create_token_for(user)}"}


# ===================================================================
# Tests
# ===================================================================


class TestListUsuarios:
    """Tests for GET /admin/usuarios."""

    def test_list_usuarios_paginated(self, session, client):
        """
        Scenario: Admin lists users with pagination
        WHEN an ADMIN calls GET /admin/usuarios?skip=0&limit=10
        THEN the system SHALL return a paginated list of users
        AND the response SHALL include total count
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )
        # Create a few extra users
        for i in range(3):
            create_user(session, email=f"user{i}@test.com")

        response = client.get(
            "/api/v1/admin/usuarios?skip=0&limit=10",
            headers=auth_header(admin),
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 4  # admin + 3 users
        assert len(data["items"]) == 4

    def test_list_usuarios_pagination_skip_limit(self, session, client):
        """
        Scenario: Admin uses skip/limit to page through users
        WHEN an ADMIN calls GET /admin/usuarios?skip=1&limit=2
        THEN the system SHALL return only the requested page
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )
        for i in range(5):
            create_user(session, email=f"user{i}@test.com")

        response = client.get(
            "/api/v1/admin/usuarios?skip=1&limit=2",
            headers=auth_header(admin),
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 6
        assert data["skip"] == 1
        assert data["limit"] == 2

    def test_search_by_nombre(self, session, client):
        """
        Scenario: Admin searches users by name
        WHEN an ADMIN calls GET /admin/usuarios?search=Juan
        THEN the system SHALL return users whose nombre or email match
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )
        create_user(session, email="juan@test.com", nombre="Juan")
        create_user(session, email="pedro@test.com", nombre="Pedro")
        create_user(session, email="jose@test.com", nombre="Jose")

        response = client.get(
            "/api/v1/admin/usuarios?search=Juan",
            headers=auth_header(admin),
        )

        assert response.status_code == 200
        data = response.json()
        # Should find both "Juan" in nombre and admin (no match)
        # Actually only juan@test.com has nombre == "Juan", admin doesn't match
        assert len(data["items"]) == 1
        assert data["items"][0]["email"] == "juan@test.com"

    def test_search_by_email(self, session, client):
        """
        Scenario: Admin searches users by email fragment
        WHEN an ADMIN calls GET /admin/usuarios?search=@test.com
        THEN the system SHALL return users whose email matches
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )
        create_user(session, email="alice@test.com")
        create_user(session, email="bob@other.com")

        response = client.get(
            "/api/v1/admin/usuarios?search=@test.com",
            headers=auth_header(admin),
        )

        assert response.status_code == 200
        data = response.json()
        # admin("admin@test.com") + alice("alice@test.com") match @test.com
        # bob("bob@other.com") does not
        assert len(data["items"]) == 2

    def test_filter_by_rol(self, session, client):
        """
        Scenario: Admin filters users by role
        WHEN an ADMIN calls GET /admin/usuarios?rol_id=2
        THEN the system SHALL return only users with that role
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )
        create_user(
            session, email="stock@test.com", rol_id=Role.STOCK.value
        )
        create_user(
            session, email="client@test.com", rol_id=Role.CLIENT.value
        )

        response = client.get(
            "/api/v1/admin/usuarios?rol_id=2",
            headers=auth_header(admin),
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["rol_id"] == 2

    def test_soft_deleted_users_are_excluded(self, session, client):
        """
        Scenario: Soft-deleted users are excluded from listing
        GIVEN a user has been soft-deleted (eliminado_en is set)
        WHEN an ADMIN lists all users
        THEN soft-deleted users SHALL NOT appear in the results
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )
        active = create_user(
            session, email="active@test.com"
        )
        deleted_user = create_user(
            session, email="deleted@test.com"
        )
        # Soft-delete one user
        deleted_user.eliminado_en = datetime.now(timezone.utc)
        session.add(deleted_user)
        session.commit()

        response = client.get(
            "/api/v1/admin/usuarios",
            headers=auth_header(admin),
        )

        assert response.status_code == 200
        data = response.json()
        emails = [u["email"] for u in data["items"]]
        assert "active@test.com" in emails
        assert "deleted@test.com" not in emails

    def test_non_admin_cannot_list_usuarios(self, session, client):
        """
        Scenario: Non-admin cannot list users
        WHEN a CLIENT user calls GET /admin/usuarios
        THEN the system SHALL return HTTP 403
        """
        client_user = create_user(
            session, email="client@test.com", rol_id=Role.CLIENT.value
        )

        response = client.get(
            "/api/v1/admin/usuarios",
            headers=auth_header(client_user),
        )

        assert response.status_code == 403

    def test_unauthenticated_request_gets_401(self, client):
        """
        Scenario: Unauthenticated request to list users
        WHEN a request without token calls GET /admin/usuarios
        THEN the system SHALL return HTTP 401
        """
        response = client.get("/api/v1/admin/usuarios")
        assert response.status_code == 401


class TestUpdateUsuario:
    """Tests for PUT /admin/usuarios/{id}."""

    def test_admin_updates_user_data(self, session, client):
        """
        Scenario: Admin updates user data
        WHEN an ADMIN sends PUT /admin/usuarios/{id} with nombre/apellido/activo
        THEN the user SHALL be updated
        AND the response SHALL contain the updated fields
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )
        target = create_user(
            session, email="target@test.com", nombre="Old", apellido="Name"
        )

        response = client.put(
            f"/api/v1/admin/usuarios/{target.id}",
            json={"nombre": "New", "apellido": "NameUpdated", "activo": False},
            headers=auth_header(admin),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "New"
        assert data["apellido"] == "NameUpdated"
        assert data["activo"] is False
        assert data["email"] == "target@test.com"

        # Verify DB was updated
        session.refresh(target)
        assert target.nombre == "New"
        assert target.activo is False

    def test_update_partial_fields(self, session, client):
        """
        Scenario: Admin updates only some user fields
        WHEN an ADMIN sends PUT /admin/usuarios/{id} with only nombre
        THEN only nombre SHALL be updated, other fields stay unchanged
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )
        target = create_user(
            session,
            email="target@test.com",
            nombre="Original",
            apellido="Lastname",
            activo=True,
        )

        response = client.put(
            f"/api/v1/admin/usuarios/{target.id}",
            json={"nombre": "Updated"},
            headers=auth_header(admin),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Updated"
        assert data["apellido"] == "Lastname"  # unchanged
        assert data["activo"] is True  # unchanged

    def test_update_nonexistent_user_returns_404(self, session, client):
        """
        Scenario: Admin tries to update non-existent user
        WHEN an ADMIN sends PUT /admin/usuarios/99999
        THEN the system SHALL return HTTP 404
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )

        response = client.put(
            "/api/v1/admin/usuarios/99999",
            json={"nombre": "Ghost"},
            headers=auth_header(admin),
        )

        assert response.status_code == 404

    def test_non_admin_cannot_update_user(self, session, client):
        """
        Scenario: Non-admin cannot update user
        WHEN a CLIENT user calls PUT /admin/usuarios/{id}
        THEN the system SHALL return HTTP 403
        """
        client_user = create_user(
            session, email="client@test.com", rol_id=Role.CLIENT.value
        )
        target = create_user(session, email="target@test.com")

        response = client.put(
            f"/api/v1/admin/usuarios/{target.id}",
            json={"nombre": "Hacker"},
            headers=auth_header(client_user),
        )

        assert response.status_code == 403


class TestSoftDeleteUsuario:
    """Tests for DELETE /admin/usuarios/{id}."""

    def test_admin_soft_deletes_user(self, session, client):
        """
        Scenario: Admin soft-deletes a user
        WHEN an ADMIN sends DELETE /admin/usuarios/{id}
        THEN the user's eliminado_en SHALL be set
        AND the response SHALL indicate success
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )
        target = create_user(session, email="delete@test.com")

        response = client.delete(
            f"/api/v1/admin/usuarios/{target.id}",
            headers=auth_header(admin),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Usuario eliminado"

        # Verify soft delete in DB
        session.refresh(target)
        assert target.eliminado_en is not None

    def test_delete_nonexistent_user_returns_404(self, session, client):
        """
        Scenario: Admin tries to delete non-existent user
        WHEN an ADMIN sends DELETE /admin/usuarios/99999
        THEN the system SHALL return HTTP 404
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )

        response = client.delete(
            "/api/v1/admin/usuarios/99999",
            headers=auth_header(admin),
        )

        assert response.status_code == 404

    def test_non_admin_cannot_soft_delete(self, session, client):
        """
        Scenario: Non-admin cannot soft-delete a user
        WHEN a CLIENT calls DELETE /admin/usuarios/{id}
        THEN the system SHALL return HTTP 403
        """
        client_user = create_user(
            session, email="client@test.com", rol_id=Role.CLIENT.value
        )
        target = create_user(session, email="target@test.com")

        response = client.delete(
            f"/api/v1/admin/usuarios/{target.id}",
            headers=auth_header(client_user),
        )

        assert response.status_code == 403
        # Verify NOT soft-deleted
        session.refresh(target)
        assert target.eliminado_en is None


class TestAssignRole:
    """Tests for PUT /admin/usuarios/{id}/role."""

    def test_admin_assigns_role_to_user(self, session, client):
        """
        Scenario: Admin assigns role to user via /admin endpoint
        WHEN an ADMIN sends PUT /admin/usuarios/{id}/role with rol_id
        THEN the user's role SHALL be updated
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )
        other_admin = create_user(
            session, email="other-admin@test.com", rol_id=Role.ADMIN.value
        )
        target = create_user(
            session, email="target@test.com", rol_id=Role.CLIENT.value
        )

        response = client.put(
            f"/api/v1/admin/usuarios/{target.id}/role",
            json={"rol_id": Role.STOCK.value},
            headers=auth_header(admin),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rol_id"] == Role.STOCK.value

        # Verify DB
        from app.domain.usuarios.repository import UsuarioRepository
        repo = UsuarioRepository(session)
        db_user = repo.get(target.id)
        assert db_user.rol_id == Role.STOCK.value

    def test_last_admin_cannot_self_degrade(self, session, client):
        """
        Scenario: Last admin cannot self-degrade (RN-RB04)
        WHEN the last ADMIN tries to change their own role away from ADMIN
        THEN the system SHALL return HTTP 400
        """
        admin = create_user(
            session, email="lonely-admin@test.com", rol_id=Role.ADMIN.value
        )
        token = create_token_for(admin)

        response = client.put(
            f"/api/v1/admin/usuarios/{admin.id}/role",
            json={"rol_id": Role.STOCK.value},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Cannot remove admin role from the last administrator"
        )

    def test_admin_can_self_degrade_with_other_admin(self, session, client):
        """
        Scenario: Admin CAN self-degrade when other admin exists
        WHEN an ADMIN with another admin in the system self-degrades
        THEN the system SHALL allow it
        """
        admin1 = create_user(
            session, email="admin1@test.com", rol_id=Role.ADMIN.value
        )
        create_user(
            session, email="admin2@test.com", rol_id=Role.ADMIN.value
        )

        response = client.put(
            f"/api/v1/admin/usuarios/{admin1.id}/role",
            json={"rol_id": Role.STOCK.value},
            headers=auth_header(admin1),
        )

        assert response.status_code == 200
        assert response.json()["rol_id"] == Role.STOCK.value

    def test_non_admin_cannot_assign_role(self, session, client):
        """
        Scenario: Non-admin cannot assign roles via /admin endpoint
        WHEN a CLIENT calls PUT /admin/usuarios/{id}/role
        THEN the system SHALL return HTTP 403
        """
        client_user = create_user(
            session, email="client@test.com", rol_id=Role.CLIENT.value
        )
        target = create_user(session, email="target@test.com")

        response = client.put(
            f"/api/v1/admin/usuarios/{target.id}/role",
            json={"rol_id": Role.ADMIN.value},
            headers=auth_header(client_user),
        )

        assert response.status_code == 403
