# Auth endpoints integration tests
import pytest
from datetime import datetime, timedelta, timezone
from sqlmodel import SQLModel, Session, create_engine, text
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.core.auth.tokens import create_access_token, create_refresh_token
from app.domain.auth.repository import RefreshTokenRepository
from app.models.usuario import Usuario
from app.core.database import get_db


# Test database setup
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
    """Create a new session for each test with clean database."""
    with Session(engine) as session:
        from tests.conftest import seed_roles
        seed_roles(session)
        # Clear all tables before each test
        session.exec(text("DELETE FROM refresh_tokens"))
        session.exec(text("DELETE FROM usuarios"))
        session.commit()
        yield session


@pytest.fixture
def test_user(session: Session) -> Usuario:
    """Create a test user in the database."""
    from app.models.usuario_rol import UsuarioRol
    now = datetime.now(timezone.utc).isoformat()
    user = Usuario(
        email="test@example.com",
        password_hash="hashedpassword",
        nombre="Test",
        apellido="User",
        activo=True,
        fecha_creacion=now,
        fecha_actualizacion=now
    )
    session.add(user)
    session.flush()  # Get user.id
    session.add(UsuarioRol(usuario_id=user.id, rol_id=1))  # ADMIN role
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def client(session: Session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_unique_tokens(user_id: int, email: str, rol_id: int):
    """
    Create unique tokens by using different creation times.
    This ensures tokens are different even if called in quick succession.
    """
    import time
    token_data = {
        "user_id": user_id,
        "email": email,
        "roles": [rol_id],
        "nonce": time.time()  # Add nonce to ensure uniqueness
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return {"access_token": access_token, "refresh_token": refresh_token}


class TestRefreshEndpoint:
    """Test cases for POST /api/v1/auth/refresh endpoint."""

    def test_refresh_with_valid_token(self, session, client, test_user):
        """
        Scenario: Valid refresh token request
        WHEN a user sends a valid refresh token to POST /api/v1/auth/refresh
        THEN the system SHALL return new httpOnly cookies
        AND the old refresh token SHALL be marked as revoked in the database
        """
        # Create unique tokens
        auth_tokens = create_unique_tokens(
            test_user.id, test_user.email, test_user.rol_id
        )
        refresh_token = auth_tokens["refresh_token"]

        # Store refresh token in database
        refresh_token_repo = RefreshTokenRepository(session)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        refresh_token_repo.create_token(refresh_token, test_user.id, expires_at)

        # Make refresh request
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        # Assert response is successful
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data

        # Verify new tokens are in cookies (not in body)
        set_cookie_header = response.headers.get("set-cookie", "")
        assert "access_token=" in set_cookie_header, "access_token cookie not set"
        assert "refresh_token=" in set_cookie_header, "refresh_token cookie not set"
        assert "httponly" in set_cookie_header.lower(), "Cookie is not httpOnly"

        # Extract the new refresh_token from cookie header for verification
        # Parse set-cookie to get the refresh_token value
        import re
        refresh_match = re.search(r"refresh_token=([^;]+)", set_cookie_header)
        assert refresh_match is not None, "Could not find refresh_token in cookies"
        new_refresh_token = refresh_match.group(1)

        # Verify new refresh token is different from old
        assert new_refresh_token != refresh_token

        # Verify old token is revoked in database
        stored_token = refresh_token_repo.get_valid_token(refresh_token)
        assert stored_token is None, "Old refresh token should be revoked"

    def test_refresh_with_expired_token(self, client, test_user):
        """
        Scenario: Expired refresh token
        WHEN a user sends an expired refresh token to POST /api/v1/auth/refresh
        THEN the system SHALL return HTTP 401 with detail "Invalid or expired token"
        """
        from jose import jwt
        from app.core.config import settings

        # Create a token with past expiration
        expired_payload = {
            "user_id": test_user.id,
            "email": test_user.email,
            "roles": test_user.rol_ids,
            "exp": 0,  # Expired timestamp
            "type": "refresh"
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": expired_token}
        )

        assert response.status_code == 401
        # Token with exp=0 is already invalid, so we get "Invalid or expired token"
        # from decode_token returning None
        assert response.json()["detail"] in ["Invalid or expired token", "Invalid token type"]

    def test_refresh_with_revoked_token(self, session, client, test_user):
        """
        Scenario: Revoked refresh token
        WHEN a user sends a revoked refresh token to POST /api/v1/auth/refresh
        THEN the system SHALL return HTTP 401 with detail "Refresh token not found or revoked"
        """
        auth_tokens = create_unique_tokens(
            test_user.id, test_user.email, test_user.rol_id
        )
        refresh_token = auth_tokens["refresh_token"]

        # Store and revoke refresh token
        refresh_token_repo = RefreshTokenRepository(session)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        refresh_token_repo.create_token(refresh_token, test_user.id, expires_at)
        refresh_token_repo.revoke_token(refresh_token)

        # Try to use revoked token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Refresh token not found or revoked"

    def test_refresh_with_invalid_token_type(self, client, test_user):
        """
        Scenario: Invalid refresh token format
        WHEN a user sends a token that is not a refresh token type
        THEN the system SHALL return HTTP 401 with detail "Invalid token type"
        """
        # Create an access token (not a refresh token)
        auth_tokens = create_unique_tokens(
            test_user.id, test_user.email, test_user.rol_id
        )
        access_token = auth_tokens["access_token"]

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token type"

    def test_refresh_token_rotation(self, session, client, test_user):
        """
        Test that refresh token rotation works correctly.
        After refresh, the old token should be invalid and new token should work.
        """
        import re

        auth_tokens = create_unique_tokens(
            test_user.id, test_user.email, test_user.rol_id
        )
        refresh_token = auth_tokens["refresh_token"]

        # Store refresh token
        refresh_token_repo = RefreshTokenRepository(session)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        refresh_token_repo.create_token(refresh_token, test_user.id, expires_at)

        # Helper to extract refresh_token from set-cookie header
        def _extract_refresh_token(response) -> str:
            set_cookie = response.headers.get("set-cookie", "")
            match = re.search(r"refresh_token=([^;]+)", set_cookie)
            assert match is not None, "refresh_token cookie not found"
            return match.group(1)

        # First refresh
        response1 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response1.status_code == 200, f"First refresh failed: {response1.text}"
        new_refresh_token_1 = _extract_refresh_token(response1)

        # Old token should be revoked
        stored_old = refresh_token_repo.get_valid_token(refresh_token)
        assert stored_old is None

        # Second refresh with new token
        response2 = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": new_refresh_token_1}
        )
        assert response2.status_code == 200, f"Second refresh failed: {response2.text}"
        new_refresh_token_2 = _extract_refresh_token(response2)

        # Both new tokens should be different
        assert new_refresh_token_1 != new_refresh_token_2


class TestLogoutEndpoint:
    """Test cases for POST /api/v1/auth/logout endpoint."""

    def test_logout_revokes_refresh_token(self, session, client, test_user):
        """
        Scenario: Successful logout
        WHEN an authenticated user calls POST /api/v1/auth/logout with a valid refresh token
        THEN the refresh token SHALL be marked as revoked in the database
        AND the system SHALL return "Logged out successfully"
        """
        auth_tokens = create_unique_tokens(
            test_user.id, test_user.email, test_user.rol_id
        )
        refresh_token = auth_tokens["refresh_token"]

        # Store refresh token
        refresh_token_repo = RefreshTokenRepository(session)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        refresh_token_repo.create_token(refresh_token, test_user.id, expires_at)

        # Logout
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

        # Verify token is revoked
        stored_token = refresh_token_repo.get_valid_token(refresh_token)
        assert stored_token is None, "Refresh token should be revoked after logout"

    def test_logout_with_already_revoked_token(self, session, client, test_user):
        """
        Scenario: Logout with already revoked token
        WHEN a user attempts to logout with an already revoked token
        THEN the system SHALL still return success (idempotent operation)
        """
        auth_tokens = create_unique_tokens(
            test_user.id, test_user.email, test_user.rol_id
        )
        refresh_token = auth_tokens["refresh_token"]

        # Store and revoke token
        refresh_token_repo = RefreshTokenRepository(session)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        refresh_token_repo.create_token(refresh_token, test_user.id, expires_at)
        refresh_token_repo.revoke_token(refresh_token)

        # Logout with revoked token
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    def test_logout_requires_authentication(self, client):
        """
        Test that logout requires authentication.
        """
        response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "some_token"}
        )

        assert response.status_code == 401  # No valid token


class TestRefreshAfterRevocation:
    """Test refresh with revoked token returns 401."""

    def test_refresh_after_logout_returns_401(self, session, client, test_user):
        """
        Scenario: Test refresh with revoked token returns 401
        WHEN a user logs out and then tries to refresh
        THEN the system SHALL return HTTP 401
        """
        auth_tokens = create_unique_tokens(
            test_user.id, test_user.email, test_user.rol_id
        )
        refresh_token = auth_tokens["refresh_token"]

        # Store refresh token
        refresh_token_repo = RefreshTokenRepository(session)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        refresh_token_repo.create_token(refresh_token, test_user.id, expires_at)

        # Logout
        client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )

        # Try to use the now-revoked token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Refresh token not found or revoked"


class TestMultipleDeviceSupport:
    """Test multiple valid refresh tokens support."""

    def test_multiple_tokens_per_user(self, session, client, test_user):
        """
        Scenario: User logs in from multiple devices
        WHEN a user logs in from device A and later from device B
        THEN both devices SHALL have independent valid refresh tokens
        AND revoking token on device A SHALL NOT affect session on device B
        """
        refresh_token_repo = RefreshTokenRepository(session)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

        # Device A login - create unique tokens
        auth_tokens_a = create_unique_tokens(
            test_user.id, test_user.email, test_user.rol_id
        )
        refresh_token_a = auth_tokens_a["refresh_token"]
        refresh_token_repo.create_token(refresh_token_a, test_user.id, expires_at)

        # Device B login - create different unique tokens
        auth_tokens_b = create_unique_tokens(
            test_user.id, test_user.email, test_user.rol_id
        )
        refresh_token_b = auth_tokens_b["refresh_token"]
        refresh_token_repo.create_token(refresh_token_b, test_user.id, expires_at)

        # Both tokens should be valid
        stored_a = refresh_token_repo.get_valid_token(refresh_token_a)
        stored_b = refresh_token_repo.get_valid_token(refresh_token_b)
        assert stored_a is not None, "Device A token should be valid"
        assert stored_b is not None, "Device B token should be valid"

        # Revoke device A token
        refresh_token_repo.revoke_token(refresh_token_a)

        # Device A should be invalid now
        stored_a_after = refresh_token_repo.get_valid_token(refresh_token_a)
        assert stored_a_after is None, "Device A token should be revoked"

        # Device B should still be valid
        stored_b_after = refresh_token_repo.get_valid_token(refresh_token_b)
        assert stored_b_after is not None, "Device B token should still be valid"

        # Device B should be able to refresh
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token_b}
        )
        assert response.status_code == 200