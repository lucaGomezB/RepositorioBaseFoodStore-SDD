"""RBAC integration tests for require_roles and admin role assignment."""
import pytest
from datetime import datetime, timezone
from sqlmodel import SQLModel, Session, create_engine, text
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from fastapi import APIRouter, Depends

from app.main import app
from app.core.auth.roles import Role
from app.core.auth.authorization import require_roles
from app.core.auth.deps import TokenPayload
from app.core.auth.tokens import create_access_token
from app.models.usuario import Usuario
from app.core.database import get_db
from app.domain.usuarios.repository import UsuarioRepository


# ---------------------------------------------------------------------------
# Test-only routes to exercise require_roles() at the HTTP layer
# ---------------------------------------------------------------------------
_test_router = APIRouter()


@_test_router.get("/require-admin")
def _test_require_admin(_: TokenPayload = Depends(require_roles(Role.ADMIN))):
    """Minimal endpoint scoped to ADMIN only."""
    return {"ok": True}


@_test_router.get("/require-stock-or-admin")
def _test_require_stock_or_admin(
    _: TokenPayload = Depends(require_roles(Role.ADMIN, Role.STOCK)),
):
    """Minimal endpoint scoped to ADMIN or STOCK."""
    return {"ok": True}


app.include_router(_test_router, prefix="/_test/rbac")


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
    """Create a clean session for each test with empty tables."""
    with Session(engine) as session:
        from tests.conftest import seed_roles
        seed_roles(session)
        session.exec(text("DELETE FROM refresh_tokens"))
        session.exec(text("DELETE FROM usuarios"))
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
    import time

    token_data = {
        "user_id": user.id,
        "email": user.email,
        "roles": user.rol_ids,
        "nonce": time.time(),
    }
    return create_access_token(token_data)


# ===================================================================
# Group 4 – Tests
# ===================================================================


class TestRequireRolesDependency:
    """Tests for the generic require_roles() dependency (4.1 – 4.3)."""

    # ------------------------------------------------------------------
    # 4.1  Test require_roles() allows access with sufficient role
    # ------------------------------------------------------------------

    def test_admin_can_access_admin_endpoint(self, session, client):
        """
        Scenario: Access allowed with sufficient role
        WHEN an authenticated user with role ADMIN accesses an endpoint
             requiring ADMIN
        THEN the system SHALL allow the request and return 200
        """
        admin = create_user(
            session, email="admin@test.com", rol_id=Role.ADMIN.value
        )
        token = create_token_for(admin)

        response = client.get(
            "/_test/rbac/require-admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"ok": True}

    # ------------------------------------------------------------------
    # 4.2  Test require_roles() denies access with insufficient role
    # ------------------------------------------------------------------

    def test_client_cannot_access_admin_endpoint(self, session, client):
        """
        Scenario: Access denied with insufficient role
        WHEN an authenticated user with role CLIENT accesses an endpoint
             requiring ADMIN
        THEN the system SHALL return HTTP 403 with 'Insufficient permissions'
        """
        client_user = create_user(
            session, email="client@test.com", rol_id=Role.CLIENT.value
        )
        token = create_token_for(client_user)

        response = client.get(
            "/_test/rbac/require-admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Insufficient permissions"

    def test_stock_cannot_access_admin_only_endpoint(self, session, client):
        """
        Scenario: STOCK role cannot access ADMIN-only endpoint
        WHEN an authenticated user with STOCK accesses /require-admin
        THEN the system SHALL return HTTP 403
        """
        stock = create_user(
            session, email="stock@test.com", rol_id=Role.STOCK.value
        )
        token = create_token_for(stock)

        response = client.get(
            "/_test/rbac/require-admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_pedidos_cannot_access_admin_endpoint(self, session, client):
        """
        Scenario: PEDIDOS role cannot access ADMIN-only endpoint
        WHEN an authenticated user with PEDIDOS accesses /require-admin
        THEN the system SHALL return HTTP 403
        """
        pedidos = create_user(
            session, email="pedidos@test.com", rol_id=Role.PEDIDOS.value
        )
        token = create_token_for(pedidos)

        response = client.get(
            "/_test/rbac/require-admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    # ------------------------------------------------------------------
    # 4.3  Test require_roles() denies access without token
    # ------------------------------------------------------------------

    def test_unauthenticated_request_gets_401(self, session, client):
        """
        Scenario: Access denied without authentication
        WHEN an unauthenticated request accesses a protected endpoint
        THEN the system SHALL return HTTP 401
        """
        response = client.get("/_test/rbac/require-admin")

        assert response.status_code == 401

    # ------------------------------------------------------------------
    # Multiple-role endpoint works for all allowed roles
    # ------------------------------------------------------------------

    def test_multiple_roles_endpoint_allows_admin(self, session, client):
        """ADMIN should pass an endpoint scoped to ADMIN|STOCK."""
        admin = create_user(
            session, email="admin-multi@test.com", rol_id=Role.ADMIN.value
        )
        token = create_token_for(admin)

        resp = client.get(
            "/_test/rbac/require-stock-or-admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200

    def test_multiple_roles_endpoint_allows_stock(self, session, client):
        """STOCK should pass an endpoint scoped to ADMIN|STOCK."""
        stock = create_user(
            session, email="stock-multi@test.com", rol_id=Role.STOCK.value
        )
        token = create_token_for(stock)

        resp = client.get(
            "/_test/rbac/require-stock-or-admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200

    def test_multiple_roles_endpoint_denies_client(self, session, client):
        """CLIENT should be denied from ADMIN|STOCK endpoint."""
        client_user = create_user(
            session,
            email="client-multi@test.com",
            rol_id=Role.CLIENT.value,
        )
        token = create_token_for(client_user)

        resp = client.get(
            "/_test/rbac/require-stock-or-admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 403


class TestAdminRoleAssignment:
    """Tests for PUT /api/v1/auth/users/{user_id}/role (4.4 – 4.6)."""

    # ------------------------------------------------------------------
    # 4.4  Test admin assigns role to another user successfully
    # ------------------------------------------------------------------

    def test_admin_assigns_role_to_another_user(self, session, client):
        """
        Scenario: Admin assigns role to user
        WHEN an authenticated ADMIN sends PUT …/users/{id}/role
             with a valid role_id
        THEN the user's role SHALL be updated
        AND  the system SHALL return the updated user
        """
        admin = create_user(
            session, email="boss@test.com", rol_id=Role.ADMIN.value
        )
        create_user(
            session, email="other-admin@test.com", rol_id=Role.ADMIN.value
        )
        target = create_user(
            session, email="target@test.com", rol_id=Role.CLIENT.value
        )
        token = create_token_for(admin)

        response = client.put(
            f"/api/v1/auth/users/{target.id}/role",
            json={"rol_id": Role.STOCK.value},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert Role.STOCK.value in data["roles"]
        assert data["email"] == target.email

        # Verify database was actually updated
        repo = UsuarioRepository(session)
        db_user = repo.get(target.id)
        assert Role.STOCK.value in db_user.rol_ids

    # ------------------------------------------------------------------
    # 4.5  Test non-admin cannot assign roles (403)
    # ------------------------------------------------------------------

    def test_non_admin_gets_403_when_assigning_role(self, session, client):
        """
        Scenario: Non-admin cannot assign roles
        WHEN a non-ADMIN user sends PUT …/users/{id}/role
        THEN the system SHALL return HTTP 403
        """
        client_user = create_user(
            session, email="regular@test.com", rol_id=Role.CLIENT.value
        )
        target = create_user(
            session, email="victim@test.com", rol_id=Role.CLIENT.value
        )
        token = create_token_for(client_user)

        response = client.put(
            f"/api/v1/auth/users/{target.id}/role",
            json={"rol_id": Role.ADMIN.value},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

        # Verify database was NOT updated
        repo = UsuarioRepository(session)
        db_user = repo.get(target.id)
        assert Role.CLIENT.value in db_user.rol_ids

    def test_stock_gets_403_when_assigning_role(self, session, client):
        """STOCK user should also be forbidden from assigning roles."""
        stock = create_user(
            session, email="stock@test.com", rol_id=Role.STOCK.value
        )
        target = create_user(
            session, email="target@test.com", rol_id=Role.CLIENT.value
        )
        token = create_token_for(stock)

        response = client.put(
            f"/api/v1/auth/users/{target.id}/role",
            json={"rol_id": Role.ADMIN.value},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    # ------------------------------------------------------------------
    # 4.6  Test last admin cannot self-degrade (400)
    # ------------------------------------------------------------------

    def test_last_admin_cannot_self_degrade(self, session, client):
        """
        Scenario: Admin prevents self-degradation as last admin
        WHEN the last ADMIN in the system attempts to change their own
             role away from ADMIN
        THEN the system SHALL return HTTP 400 with detail
             'Cannot remove admin role from the last administrator'
        """
        # Only one admin in the system – this is the "last admin"
        admin = create_user(
            session, email="lonely-admin@test.com", rol_id=Role.ADMIN.value
        )
        token = create_token_for(admin)

        response = client.put(
            f"/api/v1/auth/users/{admin.id}/role",
            json={"rol_id": Role.ADMIN.value, "action": "remove"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Cannot remove admin role from the last administrator"
        )

        # Verify database was NOT changed
        repo = UsuarioRepository(session)
        db_user = repo.get(admin.id)
        assert Role.ADMIN.value in db_user.rol_ids

    def test_last_admin_can_assign_self_to_same_role(self, session, client):
        """Last admin CAN change own role to ADMIN (no-op is fine)."""
        admin = create_user(
            session, email="stay-admin@test.com", rol_id=Role.ADMIN.value
        )
        token = create_token_for(admin)

        response = client.put(
            f"/api/v1/auth/users/{admin.id}/role",
            json={"rol_id": Role.ADMIN.value},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should succeed because they aren't changing *away from* admin
        assert response.status_code == 200
        assert Role.ADMIN.value in response.json()["roles"]

    def test_admin_can_self_degrade_when_other_admin_exists(
        self, session, client
    ):
        """Admin CAN self-degrade when another admin remains in the system."""
        admin1 = create_user(
            session, email="admin1@test.com", rol_id=Role.ADMIN.value
        )
        admin2 = create_user(
            session, email="admin2@test.com", rol_id=Role.ADMIN.value
        )
        token = create_token_for(admin1)

        # Add STOCK role
        response = client.put(
            f"/api/v1/auth/users/{admin1.id}/role",
            json={"rol_id": Role.STOCK.value, "action": "add"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert Role.STOCK.value in response.json()["roles"]

        # Remove ADMIN role (allowed because admin2 exists)
        response = client.put(
            f"/api/v1/auth/users/{admin1.id}/role",
            json={"rol_id": Role.ADMIN.value, "action": "remove"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert Role.ADMIN.value not in response.json()["roles"]

        # admin2 should still be admin
        repo = UsuarioRepository(session)
        db_admin2 = repo.get(admin2.id)
        assert Role.ADMIN.value in db_admin2.rol_ids


class TestPublicRoutes:
    """Test that public routes don't require authentication (3.1, 4.7)."""

    # ------------------------------------------------------------------
    # 4.7  Test public routes (health, login) are accessible without auth
    # ------------------------------------------------------------------

    def test_health_endpoint_accessible_without_auth(self, client):
        """
        Scenario: Health endpoint accessible without auth
        WHEN an unauthenticated request hits GET /api/v1/health
        THEN the system SHALL return 200 OK
        """
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_login_endpoint_accessible_without_auth(self, client):
        """
        Scenario: Login endpoint accessible without auth
        WHEN an unauthenticated request hits POST /api/v1/auth/login
        THEN the system SHALL process the login normally
             (proving no auth gate exists on this route)
        """
        # The endpoint processes the request and returns "Invalid credentials"
        # rather than 401 "Not authenticated" which would indicate auth is
        # required
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "anyone@test.com", "password": "wrong"},
        )

        # 401 because credentials are invalid, NOT because auth is missing
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_root_health_accessible_without_auth(self, client):
        """The /health endpoint at root level is also public."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_admin_endpoint_requires_auth(self, client):
        """A protected endpoint rejects requests without any token."""
        response = client.get("/_test/rbac/require-admin")

        assert response.status_code == 401


class TestRoleEnumValues:
    """Verify the Role IntEnum has the correct values per spec."""

    def test_role_values_match_seed(self):
        """
        Scenario: Role enum values match seed
        WHEN the Role enum is accessed
        THEN ADMIN SHALL equal 1, STOCK 2, PEDIDOS 3, CLIENT 4
        """
        assert Role.ADMIN.value == 1
        assert Role.STOCK.value == 2
        assert Role.PEDIDOS.value == 3
        assert Role.CLIENT.value == 4

    def test_role_enum_ordering(self):
        """IntEnum ordering matches the numeric values."""
        roles = sorted(Role)
        assert roles == [Role.ADMIN, Role.STOCK, Role.PEDIDOS, Role.CLIENT]
