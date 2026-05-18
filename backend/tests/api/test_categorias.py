# Categorias endpoints integration tests
import pytest
from datetime import datetime, timezone
from sqlmodel import SQLModel, Session, create_engine, text
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import time

from app.main import app
from app.core.auth.tokens import create_access_token
from app.models.categoria import Categoria
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
        session.exec(text("DELETE FROM categorias"))
        session.commit()
        yield session


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


def make_token(user_id: int, email: str, rol_id: int) -> str:
    """Create an access token for testing."""
    token_data = {
        "user_id": user_id,
        "email": email,
        "roles": [rol_id],
        "nonce": time.time(),
    }
    return create_access_token(token_data)


# --- Fixtures for auth tokens ---

@pytest.fixture
def admin_token() -> str:
    """Token for ADMIN user (rol_id=1)."""
    return make_token(user_id=1, email="admin@test.com", rol_id=1)


@pytest.fixture
def stock_token() -> str:
    """Token for STOCK user (rol_id=2)."""
    return make_token(user_id=2, email="stock@test.com", rol_id=2)


@pytest.fixture
def client_token() -> str:
    """Token for CLIENT user (rol_id=4) — should be denied."""
    return make_token(user_id=3, email="client@test.com", rol_id=4)


# --- Tests ---

class TestCategoriasPublic:
    """Tests for public GET endpoints (no auth required)."""

    def test_get_empty_tree(self, client):
        """GET /categorias with no categories returns empty list."""
        response = client.get("/api/v1/categorias/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_public_tree(self, session, client):
        """GET /categorias returns hierarchical tree structure."""
        now = datetime.now(timezone.utc).isoformat()
        root = Categoria(
            nombre="Bebidas",
            descripcion="Bebidas gaseosas y naturales",
            orden_display=1,
            fecha_creacion=now,
            fecha_actualizacion=now,
        )
        session.add(root)
        session.commit()
        session.refresh(root)

        child = Categoria(
            nombre="Gaseosas",
            descripcion="Bebidas carbonatadas",
            parent_id=root.id,
            orden_display=1,
            fecha_creacion=now,
            fecha_actualizacion=now,
        )
        session.add(child)
        session.commit()

        response = client.get("/api/v1/categorias/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["nombre"] == "Bebidas"
        assert len(data[0]["subcategorias"]) == 1
        assert data[0]["subcategorias"][0]["nombre"] == "Gaseosas"

    def test_get_category_by_id(self, session, client):
        """GET /categorias/{id} returns single category."""
        now = datetime.now(timezone.utc).isoformat()
        cat = Categoria(nombre="Postres", fecha_creacion=now, fecha_actualizacion=now)
        session.add(cat)
        session.commit()
        session.refresh(cat)

        response = client.get(f"/api/v1/categorias/{cat.id}")
        assert response.status_code == 200
        assert response.json()["nombre"] == "Postres"

    def test_get_category_by_id_not_found(self, client):
        """GET /categorias/{id} returns 404 for non-existent category."""
        response = client.get("/api/v1/categorias/9999")
        assert response.status_code == 404

    def test_soft_deleted_category_hidden_from_public(self, session, client):
        """Soft-deleted categories should not appear in public tree."""
        now = datetime.now(timezone.utc).isoformat()
        cat = Categoria(nombre="Oculta", fecha_creacion=now, fecha_actualizacion=now)
        session.add(cat)
        session.commit()
        session.refresh(cat)

        # Soft delete
        cat_db = session.get(Categoria, cat.id)
        cat_db.eliminado_en = now
        cat_db.fecha_actualizacion = now
        session.commit()

        # Should not appear in tree
        response = client.get("/api/v1/categorias/")
        assert response.status_code == 200
        names = [c["nombre"] for c in response.json()]
        assert "Oculta" not in names


class TestCategoriasCreate:
    """Tests for POST /categorias (requires auth)."""

    def test_create_root_category(self, session, client, admin_token):
        """POST /categorias with just nombre creates root category."""
        response = client.post(
            "/api/v1/categorias/",
            json={"nombre": "Entrantes"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Entrantes"
        assert data["parent_id"] is None

    def test_create_subcategory(self, session, client, admin_token):
        """POST /categorias with parent_id creates subcategory."""
        now = datetime.now(timezone.utc).isoformat()
        parent = Categoria(nombre="Bebidas", fecha_creacion=now, fecha_actualizacion=now)
        session.add(parent)
        session.commit()
        session.refresh(parent)

        response = client.post(
            "/api/v1/categorias/",
            json={"nombre": "Jugos", "parent_id": parent.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Jugos"
        assert data["parent_id"] == parent.id

    def test_create_category_with_invalid_parent(self, client, admin_token):
        """POST with non-existent parent_id returns 400."""
        response = client.post(
            "/api/v1/categorias/",
            json={"nombre": "Test", "parent_id": 9999},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400
        assert "Parent category not found" in response.json()["detail"]

    def test_create_duplicate_name(self, session, client, admin_token):
        """POST with duplicate name returns 400."""
        now = datetime.now(timezone.utc).isoformat()
        cat = Categoria(nombre="Unico", fecha_creacion=now, fecha_actualizacion=now)
        session.add(cat)
        session.commit()

        response = client.post(
            "/api/v1/categorias/",
            json={"nombre": "Unico"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_non_stock_cannot_create(self, client, client_token):
        """POST with CLIENT token returns 403."""
        response = client.post(
            "/api/v1/categorias/",
            json={"nombre": "NoPermitido"},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        assert response.status_code == 403

    def test_unauthenticated_cannot_create(self, client):
        """POST without token returns 401."""
        response = client.post(
            "/api/v1/categorias/",
            json={"nombre": "SinAuth"},
        )
        assert response.status_code == 401


class TestCategoriasUpdate:
    """Tests for PUT /categorias/{id} (requires auth)."""

    def test_update_category_name(self, session, client, admin_token):
        """PUT /categorias/{id} changes the name."""
        now = datetime.now(timezone.utc).isoformat()
        cat = Categoria(nombre="Viejo", fecha_creacion=now, fecha_actualizacion=now)
        session.add(cat)
        session.commit()
        session.refresh(cat)

        response = client.put(
            f"/api/v1/categorias/{cat.id}",
            json={"nombre": "Nuevo"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Nuevo"

    def test_cannot_set_self_as_parent(self, session, client, admin_token):
        """PUT that tries to set category as its own parent returns 400."""
        now = datetime.now(timezone.utc).isoformat()
        cat = Categoria(nombre="Solo", fecha_creacion=now, fecha_actualizacion=now)
        session.add(cat)
        session.commit()
        session.refresh(cat)

        response = client.put(
            f"/api/v1/categorias/{cat.id}",
            json={"parent_id": cat.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400
        assert "own parent" in response.json()["detail"]

    def test_cannot_create_cycle(self, session, client, admin_token):
        """Cannot set parent to a descendant (creates cycle)."""
        now = datetime.now(timezone.utc).isoformat()
        parent = Categoria(nombre="Padre", fecha_creacion=now, fecha_actualizacion=now)
        session.add(parent)
        session.commit()
        session.refresh(parent)

        child = Categoria(
            nombre="Hijo", parent_id=parent.id,
            fecha_creacion=now, fecha_actualizacion=now,
        )
        session.add(child)
        session.commit()
        session.refresh(child)

        # Try to set parent as child of itself → cycle
        response = client.put(
            f"/api/v1/categorias/{parent.id}",
            json={"parent_id": child.id},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400
        assert "circular reference" in response.json()["detail"]

    def test_update_with_invalid_parent(self, session, client, admin_token):
        """PUT with non-existent parent_id returns 400."""
        now = datetime.now(timezone.utc).isoformat()
        cat = Categoria(nombre="Test", fecha_creacion=now, fecha_actualizacion=now)
        session.add(cat)
        session.commit()
        session.refresh(cat)

        response = client.put(
            f"/api/v1/categorias/{cat.id}",
            json={"parent_id": 9999},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400
        assert "Parent category not found" in response.json()["detail"]


class TestCategoriasDelete:
    """Tests for DELETE /categorias/{id} (requires auth)."""

    def test_soft_delete_marks_eliminado_en(self, session, client, admin_token):
        """DELETE sets eliminado_en and hides from public tree."""
        now = datetime.now(timezone.utc).isoformat()
        cat = Categoria(nombre="Eliminar", fecha_creacion=now, fecha_actualizacion=now)
        session.add(cat)
        session.commit()
        session.refresh(cat)

        response = client.delete(
            f"/api/v1/categorias/{cat.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["eliminado_en"] is not None

        # Should be hidden from public tree
        get_response = client.get("/api/v1/categorias/")
        names = [c["nombre"] for c in get_response.json()]
        assert "Eliminar" not in names

    def test_delete_non_existent_returns_404(self, client, admin_token):
        """DELETE on non-existent category returns 404."""
        response = client.delete(
            "/api/v1/categorias/9999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_stock_can_delete(self, session, client, stock_token):
        """STOCK user can also delete categories."""
        now = datetime.now(timezone.utc).isoformat()
        cat = Categoria(nombre="StockDel", fecha_creacion=now, fecha_actualizacion=now)
        session.add(cat)
        session.commit()
        session.refresh(cat)

        response = client.delete(
            f"/api/v1/categorias/{cat.id}",
            headers={"Authorization": f"Bearer {stock_token}"},
        )
        assert response.status_code == 200

    def test_unauthenticated_cannot_delete(self, client):
        """DELETE without token returns 401."""
        response = client.delete("/api/v1/categorias/1")
        assert response.status_code == 401
