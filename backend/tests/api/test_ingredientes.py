# Ingredientes endpoints integration tests
import pytest
from datetime import datetime, timezone
from sqlmodel import SQLModel, Session, create_engine, text
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import time

from app.main import app
from app.core.auth.tokens import create_access_token
from app.models.ingrediente import Ingrediente
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
        session.exec(text("DELETE FROM ingredientes"))
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
        "rol_id": rol_id,
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


# --- Fixtures for test data ---

@pytest.fixture
def sample_ingredients(session):
    """Create sample ingredients for testing."""
    now = datetime.now(timezone.utc).isoformat()
    ing1 = Ingrediente(
        nombre="Harina",
        descripcion="Harina de trigo 0000",
        es_alergeno=True,
        fecha_creacion=now,
        fecha_actualizacion=now,
    )
    ing2 = Ingrediente(
        nombre="Azucar",
        descripcion="Azúcar blanca refinada",
        es_alergeno=False,
        fecha_creacion=now,
        fecha_actualizacion=now,
    )
    ing3 = Ingrediente(
        nombre="Leche",
        descripcion="Leche entera pasteurizada",
        es_alergeno=True,
        fecha_creacion=now,
        fecha_actualizacion=now,
    )
    session.add(ing1)
    session.add(ing2)
    session.add(ing3)
    session.commit()
    for ing in [ing1, ing2, ing3]:
        session.refresh(ing)
    return ing1, ing2, ing3


# --- Tests ---

class TestIngredientesPublic:
    """Tests for public GET endpoints (no auth required)."""

    def test_get_empty_list(self, client):
        """GET /ingredientes with no ingredients returns empty list."""
        response = client.get("/api/v1/ingredientes/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_ingredients(self, client, sample_ingredients):
        """GET /ingredientes returns all non-deleted ingredients."""
        response = client.get("/api/v1/ingredientes/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = [i["nombre"] for i in data]
        assert "Harina" in names
        assert "Azucar" in names
        assert "Leche" in names

    def test_filter_by_es_alergeno_true(self, client, sample_ingredients):
        """GET /ingredientes?es_alergeno=true filters ingredients."""
        response = client.get("/api/v1/ingredientes/?es_alergeno=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for ing in data:
            assert ing["es_alergeno"] is True

    def test_filter_by_es_alergeno_false(self, client, sample_ingredients):
        """GET /ingredientes?es_alergeno=false filters ingredients."""
        response = client.get("/api/v1/ingredientes/?es_alergeno=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["nombre"] == "Azucar"
        assert data[0]["es_alergeno"] is False

    def test_get_ingredient_by_id(self, client, sample_ingredients):
        """GET /ingredientes/{id} returns single ingredient."""
        ing1, _, _ = sample_ingredients
        response = client.get(f"/api/v1/ingredientes/{ing1.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Harina"
        assert data["es_alergeno"] is True

    def test_get_ingredient_by_id_not_found(self, client):
        """GET /ingredientes/{id} returns 404 for non-existent ingredient."""
        response = client.get("/api/v1/ingredientes/9999")
        assert response.status_code == 404

    def test_soft_deleted_ingredient_hidden_from_public(self, client, session, sample_ingredients):
        """Soft-deleted ingredients should not appear in public list."""
        ing1, _, _ = sample_ingredients

        # Soft delete
        now = datetime.now(timezone.utc).isoformat()
        ing1_db = session.get(Ingrediente, ing1.id)
        ing1_db.eliminado_en = now
        ing1_db.fecha_actualizacion = now
        session.commit()

        # Should not appear in list
        response = client.get("/api/v1/ingredientes/")
        assert response.status_code == 200
        names = [i["nombre"] for i in response.json()]
        assert "Harina" not in names

    def test_soft_deleted_ingredient_not_found_by_id(self, client, session, sample_ingredients):
        """GET soft-deleted ingredient by ID returns 404."""
        ing1, _, _ = sample_ingredients

        now = datetime.now(timezone.utc).isoformat()
        ing1_db = session.get(Ingrediente, ing1.id)
        ing1_db.eliminado_en = now
        ing1_db.fecha_actualizacion = now
        session.commit()

        response = client.get(f"/api/v1/ingredientes/{ing1.id}")
        assert response.status_code == 404


class TestIngredientesCreate:
    """Tests for POST /ingredientes (requires auth)."""

    def test_create_ingredient_without_allergen(self, client, admin_token):
        """POST /ingredientes creates ingredient with es_alergeno=false by default."""
        response = client.post(
            "/api/v1/ingredientes/",
            json={"nombre": "Sal", "descripcion": "Sal fina"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Sal"
        assert data["descripcion"] == "Sal fina"
        assert data["es_alergeno"] is False

    def test_create_ingredient_with_allergen(self, client, admin_token):
        """POST /ingredientes with es_alergeno=true."""
        response = client.post(
            "/api/v1/ingredientes/",
            json={"nombre": "Maní", "es_alergeno": True},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Maní"
        assert data["es_alergeno"] is True

    def test_create_duplicate_name(self, session, client, admin_token):
        """POST with duplicate name returns 400."""
        now = datetime.now(timezone.utc).isoformat()
        ing = Ingrediente(nombre="Unico", fecha_creacion=now, fecha_actualizacion=now)
        session.add(ing)
        session.commit()

        response = client.post(
            "/api/v1/ingredientes/",
            json={"nombre": "Unico"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_ingredient_name_too_short(self, client, admin_token):
        """POST with name too short returns 422."""
        response = client.post(
            "/api/v1/ingredientes/",
            json={"nombre": "A"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 422

    def test_non_stock_cannot_create(self, client, client_token):
        """POST with CLIENT token returns 403."""
        response = client.post(
            "/api/v1/ingredientes/",
            json={"nombre": "NoPermitido"},
            headers={"Authorization": f"Bearer {client_token}"},
        )
        assert response.status_code == 403

    def test_unauthenticated_cannot_create(self, client):
        """POST without token returns 401."""
        response = client.post(
            "/api/v1/ingredientes/",
            json={"nombre": "SinAuth"},
        )
        assert response.status_code == 401


class TestIngredientesUpdate:
    """Tests for PUT /ingredientes/{id} (requires auth)."""

    def test_update_ingredient_name(self, session, client, admin_token):
        """PUT /ingredientes/{id} changes the name."""
        now = datetime.now(timezone.utc).isoformat()
        ing = Ingrediente(nombre="Viejo", fecha_creacion=now, fecha_actualizacion=now)
        session.add(ing)
        session.commit()
        session.refresh(ing)

        response = client.put(
            f"/api/v1/ingredientes/{ing.id}",
            json={"nombre": "Nuevo"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Nuevo"

    def test_update_ingredient_allergen_flag(self, session, client, admin_token):
        """PUT /ingredientes/{id} changes es_alergeno."""
        now = datetime.now(timezone.utc).isoformat()
        ing = Ingrediente(
            nombre="Cambiante", es_alergeno=False,
            fecha_creacion=now, fecha_actualizacion=now,
        )
        session.add(ing)
        session.commit()
        session.refresh(ing)

        response = client.put(
            f"/api/v1/ingredientes/{ing.id}",
            json={"es_alergeno": True},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["es_alergeno"] is True

    def test_update_duplicate_name(self, session, client, admin_token):
        """PUT with name that conflicts with existing returns 400."""
        now = datetime.now(timezone.utc).isoformat()
        ing1 = Ingrediente(nombre="Primero", fecha_creacion=now, fecha_actualizacion=now)
        ing2 = Ingrediente(nombre="Segundo", fecha_creacion=now, fecha_actualizacion=now)
        session.add(ing1)
        session.add(ing2)
        session.commit()
        session.refresh(ing1)
        session.refresh(ing2)

        response = client.put(
            f"/api/v1/ingredientes/{ing2.id}",
            json={"nombre": "Primero"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_update_non_existent_returns_404(self, client, admin_token):
        """PUT on non-existent ingredient returns 404."""
        response = client.put(
            "/api/v1/ingredientes/9999",
            json={"nombre": "Nope"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_unauthenticated_cannot_update(self, client):
        """PUT without token returns 401."""
        response = client.put(
            "/api/v1/ingredientes/1",
            json={"nombre": "Nope"},
        )
        assert response.status_code == 401


class TestIngredientesDelete:
    """Tests for DELETE /ingredientes/{id} (requires auth)."""

    def test_soft_delete_marks_eliminado_en(self, session, client, admin_token):
        """DELETE sets eliminado_en and hides from public list."""
        now = datetime.now(timezone.utc).isoformat()
        ing = Ingrediente(nombre="Eliminar", fecha_creacion=now, fecha_actualizacion=now)
        session.add(ing)
        session.commit()
        session.refresh(ing)

        response = client.delete(
            f"/api/v1/ingredientes/{ing.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["eliminado_en"] is not None

        # Should be hidden from public list
        get_response = client.get("/api/v1/ingredientes/")
        names = [i["nombre"] for i in get_response.json()]
        assert "Eliminar" not in names

    def test_delete_non_existent_returns_404(self, client, admin_token):
        """DELETE on non-existent ingredient returns 404."""
        response = client.delete(
            "/api/v1/ingredientes/9999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_stock_can_delete(self, session, client, stock_token):
        """STOCK user can also delete ingredients."""
        now = datetime.now(timezone.utc).isoformat()
        ing = Ingrediente(nombre="StockDel", fecha_creacion=now, fecha_actualizacion=now)
        session.add(ing)
        session.commit()
        session.refresh(ing)

        response = client.delete(
            f"/api/v1/ingredientes/{ing.id}",
            headers={"Authorization": f"Bearer {stock_token}"},
        )
        assert response.status_code == 200

    def test_unauthenticated_cannot_delete(self, client):
        """DELETE without token returns 401."""
        response = client.delete("/api/v1/ingredientes/1")
        assert response.status_code == 401
