"""Integration tests for Productos CRUD endpoints (stock, soft delete, roles, filters, relationships)."""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from sqlmodel import SQLModel, Session, create_engine, text
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.core.auth.roles import Role
from app.core.auth.tokens import create_access_token
from app.models.usuario import Usuario
from app.models.producto import Producto
from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente
from app.models.producto_categoria import ProductoCategoria
from app.models.producto_ingrediente import ProductoIngrediente
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


def create_categoria(session: Session, **overrides) -> Categoria:
    """Factory helper to create a Categoria row."""
    defaults = dict(nombre="Test Categoria", descripcion="A test category")
    defaults.update(overrides)
    cat = Categoria(**defaults)
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


def create_ingrediente(session: Session, **overrides) -> Ingrediente:
    """Factory helper to create an Ingrediente row."""
    defaults = dict(nombre="Test Ingrediente", descripcion="A test ingredient")
    defaults.update(overrides)
    ing = Ingrediente(**defaults)
    session.add(ing)
    session.commit()
    session.refresh(ing)
    return ing


def _create_minimal_product_payload(
    categoria_id: int,
    ingrediente_id: int,
    **overrides,
) -> dict:
    """Return a valid product creation payload."""
    defaults = dict(
        nombre="Pizza Test",
        descripcion="Una pizza de prueba",
        precio_base=12.50,
        stock_cantidad=10,
        disponible=True,
        tiempo_prep_min=15,
        categorias_ids=[categoria_id],
        categoria_principal_id=categoria_id,
        ingredientes=[
            {
                "ingrediente_id": ingrediente_id,
                "es_removible": True,
                "es_principal": True,
                "orden": 0,
            }
        ],
    )
    defaults.update(overrides)
    return defaults


def create_producto_in_db(
    session: Session,
    **overrides,
) -> Producto:
    """Create a Producto directly in the DB (bypassing API)."""
    now_str = datetime.now(timezone.utc).isoformat()
    defaults = dict(
        nombre="DB Product",
        descripcion="Created directly in DB",
        precio_base=Decimal("9.99"),
        stock_cantidad=5,
        disponible=True,
        tiempo_prep_min=10,
        fecha_creacion=now_str,
        fecha_actualizacion=now_str,
    )
    defaults.update(overrides)
    prod = Producto(**defaults)
    session.add(prod)
    session.commit()
    session.refresh(prod)
    return prod


# ===================================================================
# Tests
# ===================================================================


class TestCreateProducto:
    """Tests for POST /api/v1/productos."""

    def test_create_producto_with_stock_valido(
        self, session, client
    ):
        """
        Scenario: 5.1 Crear producto con stock_cantidad válido
        WHEN an ADMIN sends POST with stock_cantidad=10
        THEN the system SHALL return HTTP 201 with stock_cantidad=10
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)
        cat = create_categoria(session)
        ing = create_ingrediente(session)

        payload = _create_minimal_product_payload(
            categoria_id=cat.id,
            ingrediente_id=ing.id,
            stock_cantidad=10,
        )

        response = client.post(
            "/api/v1/productos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["stock_cantidad"] == 10
        assert data["nombre"] == "Pizza Test"

    def test_create_producto_stock_negativo_returns_422(
        self, session, client
    ):
        """
        Scenario: 5.2 Crear producto con stock negativo devuelve 422
        WHEN an ADMIN sends POST with stock_cantidad=-1
        THEN the system SHALL return HTTP 422
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)
        cat = create_categoria(session)
        ing = create_ingrediente(session)

        payload = _create_minimal_product_payload(
            categoria_id=cat.id,
            ingrediente_id=ing.id,
            stock_cantidad=-1,
        )

        response = client.post(
            "/api/v1/productos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422

    def test_client_cannot_create_product(
        self, session, client
    ):
        """
        Scenario: Client cannot create product
        WHEN a CLIENT sends POST
        THEN the system SHALL return HTTP 403
        """
        client_user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(client_user)
        cat = create_categoria(session)
        ing = create_ingrediente(session)

        payload = _create_minimal_product_payload(
            categoria_id=cat.id,
            ingrediente_id=ing.id,
        )

        response = client.post(
            "/api/v1/productos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_stock_can_create_product(
        self, session, client
        ):
        """
        Scenario: STOCK role can create product
        WHEN a STOCK user sends POST
        THEN the system SHALL return HTTP 201
        """
        stock = create_user(session, rol_id=Role.STOCK.value)
        token = create_token_for(stock)
        cat = create_categoria(session)
        ing = create_ingrediente(session)

        payload = _create_minimal_product_payload(
            categoria_id=cat.id,
            ingrediente_id=ing.id,
        )

        response = client.post(
            "/api/v1/productos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201


class TestSoftDelete:
    """Tests for DELETE /api/v1/productos/{id} (soft delete)."""

    def test_soft_delete_producto(self, session, client):
        """
        Scenario: 5.3 Soft delete producto
        WHEN an ADMIN sends DELETE
        THEN the system SHALL set eliminado_en and return 204
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)
        prod = create_producto_in_db(session)

        response = client.delete(
            f"/api/v1/productos/{prod.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

        # Verify the product was soft-deleted in DB
        session.expire_all()
        deleted = session.get(Producto, prod.id)
        assert deleted is not None
        assert deleted.eliminado_en is not None

    def test_soft_deleted_product_excluded_from_list(
        self, session, client
    ):
        """
        Scenario: Deleted product excluded from list
        WHEN a user calls GET /api/v1/productos after soft delete
        THEN the deleted product SHALL NOT appear
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)
        prod = create_producto_in_db(session)

        # Soft delete
        client.delete(
            f"/api/v1/productos/{prod.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # List all
        response = client.get("/api/v1/productos/")
        assert response.status_code == 200
        ids = [p["id"] for p in response.json()]
        assert prod.id not in ids

    def test_soft_delete_nonexistent_product(
        self, session, client
    ):
        """
        Scenario: Soft delete nonexistent product → 404
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)

        response = client.delete(
            "/api/v1/productos/99999",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404


class TestUpdateStock:
    """Tests for PATCH /api/v1/productos/{id}/stock."""

    def test_increment_stock(self, session, client):
        """
        Scenario: 5.4 Incrementar stock atómicamente
        WHEN an ADMIN sends PATCH /stock with cantidad=10
        THEN stock_cantidad SHALL increment by 10
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)
        prod = create_producto_in_db(session, stock_cantidad=5)

        response = client.patch(
            f"/api/v1/productos/{prod.id}/stock",
            json={"cantidad": 10},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stock_cantidad"] == 15

    def test_decrement_stock(self, session, client):
        """
        Scenario: Decrementar stock
        WHEN an ADMIN sends PATCH /stock with cantidad=-5 on stock=10
        THEN stock_cantidad SHALL become 5
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)
        prod = create_producto_in_db(session, stock_cantidad=10)

        response = client.patch(
            f"/api/v1/productos/{prod.id}/stock",
            json={"cantidad": -5},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stock_cantidad"] == 5

    def test_decrement_below_zero_rejected(self, session, client):
        """
        Scenario: 5.5 Decrementar stock por debajo de cero es rechazado
        WHEN stock=5 and cantidad=-100
        THEN return 400 with "Insufficient stock"
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)
        prod = create_producto_in_db(session, stock_cantidad=5)

        response = client.patch(
            f"/api/v1/productos/{prod.id}/stock",
            json={"cantidad": -100},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]

    def test_update_stock_nonexistent_product(self, session, client):
        """
        Scenario: Update stock on nonexistent product → 404
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)

        response = client.patch(
            "/api/v1/productos/99999/stock",
            json={"cantidad": 10},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404


class TestRoles:
    """Tests for role-based access control on productos endpoints."""

    def test_endpoint_requiere_roles_admin_o_stock(self, session, client):
        """
        Scenario: 5.6 Endpoint requiere roles [ADMIN, STOCK]
        WHEN a CLIENT tries to create/update/delete
        THEN return 403
        """
        client_user = create_user(session, rol_id=Role.CLIENT.value)
        token = create_token_for(client_user)
        cat = create_categoria(session)
        ing = create_ingrediente(session)

        payload = _create_minimal_product_payload(
            categoria_id=cat.id,
            ingrediente_id=ing.id,
        )

        # Create
        resp = client.post(
            "/api/v1/productos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

        # Update
        prod = create_producto_in_db(session)
        resp = client.patch(
            f"/api/v1/productos/{prod.id}",
            json={"nombre": "Hacked"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

        # Delete
        resp = client.delete(
            f"/api/v1/productos/{prod.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    def test_stock_role_can_create_update_delete(self, session, client):
        """
        STOCK role should be able to create, update, and soft-delete.
        """
        stock = create_user(session, rol_id=Role.STOCK.value)
        token = create_token_for(stock)
        cat = create_categoria(session)
        ing = create_ingrediente(session)

        payload = _create_minimal_product_payload(
            categoria_id=cat.id,
            ingrediente_id=ing.id,
        )

        # Create
        resp = client.post(
            "/api/v1/productos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        prod_id = resp.json()["id"]

        # Update
        resp = client.patch(
            f"/api/v1/productos/{prod_id}",
            json={"nombre": "Updated by Stock"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

        # Delete
        resp = client.delete(
            f"/api/v1/productos/{prod_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204


class TestFilters:
    """Tests for GET /api/v1/productos with query params."""

    def test_filter_by_categoria_id(self, session, client):
        """
        Scenario: 5.7 Filtrar por categoria_id
        WHEN GET /api/v1/productos?categoria_id=...
        THEN return only products in that category
        """
        # Import needed service
        from app.core.services.producto import ProductoService
        from app.core.repositories.producto import ProductoRepository

        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)

        # Create two categories
        cat1 = create_categoria(session, nombre="Cat1")
        cat2 = create_categoria(session, nombre="Cat2")
        ing = create_ingrediente(session)

        # Create product in cat1 via API
        payload1 = _create_minimal_product_payload(
            categoria_id=cat1.id,
            ingrediente_id=ing.id,
            nombre="Producto Cat1",
        )
        resp = client.post(
            "/api/v1/productos/",
            json=payload1,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201

        # Create product in cat2 via API
        payload2 = _create_minimal_product_payload(
            categoria_id=cat2.id,
            ingrediente_id=ing.id,
            nombre="Producto Cat2",
        )
        resp = client.post(
            "/api/v1/productos/",
            json=payload2,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201

        # Filter by cat1
        response = client.get(f"/api/v1/productos/?categoria_id={cat1.id}")
        assert response.status_code == 200
        data = response.json()
        names = [p["nombre"] for p in data]
        assert "Producto Cat1" in names
        assert "Producto Cat2" not in names

    def test_filter_by_busqueda(self, session, client):
        """
        Scenario: Filtrar por busqueda (nombre ILIKE)
        WHEN GET /api/v1/productos?busqueda=pizza
        THEN return products whose nombre contains "pizza"
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)
        cat = create_categoria(session)
        ing = create_ingrediente(session)

        payload1 = _create_minimal_product_payload(
            categoria_id=cat.id,
            ingrediente_id=ing.id,
            nombre="Pizza Margherita",
        )
        client.post(
            "/api/v1/productos/",
            json=payload1,
            headers={"Authorization": f"Bearer {token}"},
        )

        payload2 = _create_minimal_product_payload(
            categoria_id=cat.id,
            ingrediente_id=ing.id,
            nombre="Ensalada Caesar",
        )
        client.post(
            "/api/v1/productos/",
            json=payload2,
            headers={"Authorization": f"Bearer {token}"},
        )

        response = client.get("/api/v1/productos/?busqueda=pizza")
        assert response.status_code == 200
        data = response.json()
        names = [p["nombre"] for p in data]
        assert "Pizza Margherita" in names
        assert "Ensalada Caesar" not in names

    def test_filter_by_disponible(self, session, client):
        """
        Scenario: Filtrar por disponible
        WHEN GET /api/v1/productos?disponible=false
        THEN return only non-available products
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)
        cat = create_categoria(session)
        ing = create_ingrediente(session)

        payload1 = _create_minimal_product_payload(
            categoria_id=cat.id,
            ingrediente_id=ing.id,
            nombre="Disponible",
            disponible=True,
        )
        client.post(
            "/api/v1/productos/",
            json=payload1,
            headers={"Authorization": f"Bearer {token}"},
        )

        payload2 = _create_minimal_product_payload(
            categoria_id=cat.id,
            ingrediente_id=ing.id,
            nombre="No Disponible",
            disponible=False,
        )
        client.post(
            "/api/v1/productos/",
            json=payload2,
            headers={"Authorization": f"Bearer {token}"},
        )

        response = client.get("/api/v1/productos/?disponible=false")
        assert response.status_code == 200
        data = response.json()
        names = [p["nombre"] for p in data]
        assert "No Disponible" in names
        assert "Disponible" not in names


class TestGetSingleProduct:
    """Tests for GET /api/v1/productos/{id}."""

    def test_get_deleted_product_returns_404(self, session, client):
        """
        A soft-deleted product should not be found via GET by ID.
        """
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)
        prod = create_producto_in_db(session)

        # Soft delete
        client.delete(
            f"/api/v1/productos/{prod.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Try to get it
        response = client.get(f"/api/v1/productos/{prod.id}")
        assert response.status_code == 404

    def test_get_existing_product_returns_200(self, session, client):
        """Get an existing product returns 200 with all fields."""
        prod = create_producto_in_db(session)

        response = client.get(f"/api/v1/productos/{prod.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == prod.id
        assert "stock_cantidad" in data
        assert data["stock_cantidad"] == prod.stock_cantidad


# ===================================================================
# Tests for Producto Relationships (ingredients and categories)
# ===================================================================


class TestProductoRelaciones:
    """Tests for relationship management endpoints (GET, POST, PUT, DELETE)."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _create_admin(self, session):
        """Create an admin user and return (user, token)."""
        admin = create_user(session, rol_id=Role.ADMIN.value)
        token = create_token_for(admin)
        return admin, token

    def _create_product_via_api(
        self, client, session, token: str,
        nombre="Pizza Relaciones", ingrediente_id=None, categoria_id=None,
    ) -> dict:
        """Create a product via API and return the response data."""
        if ingrediente_id is None:
            ing = create_ingrediente(session)
            ingrediente_id = ing.id
        if categoria_id is None:
            cat = create_categoria(session)
            categoria_id = cat.id

        payload = {
            "nombre": nombre,
            "descripcion": "Test de relaciones",
            "precio_base": 10.0,
            "stock_cantidad": 5,
            "disponible": True,
            "tiempo_prep_min": 10,
            "categorias_ids": [categoria_id],
            "categoria_principal_id": categoria_id,
            "ingredientes": [
                {
                    "ingrediente_id": ingrediente_id,
                    "es_removible": True,
                    "es_principal": True,
                    "orden": 0,
                }
            ],
        }
        resp = client.post(
            "/api/v1/productos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        return resp.json()

    # ------------------------------------------------------------------
    # 4.1 — PUT ingredientes reemplaza correctamente
    # ------------------------------------------------------------------

    def test_put_ingredientes_reemplaza_correctamente(
        self, session, client
    ):
        """
        WHEN admin sends PUT /productos/{id}/ingredientes with 2 ingredients
        THEN all existing ingredients are replaced and 200 is returned
        """
        admin, token = self._create_admin(session)

        # Create 2 ingredients
        ing1 = create_ingrediente(session, nombre="Ing1")
        ing2 = create_ingrediente(session, nombre="Ing2")

        # Create product via API (gets 1 ingredient assigned)
        producto = self._create_product_via_api(
            client, session, token, ingrediente_id=ing1.id,
        )

        # PUT replaces with both ingredients
        payload = [
            {"ingrediente_id": ing1.id, "es_removible": True, "es_principal": False, "orden": 1},
            {"ingrediente_id": ing2.id, "es_removible": True, "es_principal": True, "orden": 0},
        ]
        resp = client.put(
            f"/api/v1/productos/{producto['id']}/ingredientes",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        ing_ids = [item["ingrediente_id"] for item in data]
        assert ing1.id in ing_ids
        assert ing2.id in ing_ids

    # ------------------------------------------------------------------
    # 4.2 — PUT categorías reemplaza correctamente
    # ------------------------------------------------------------------

    def test_put_categorias_reemplaza_correctamente(
        self, session, client
    ):
        """
        WHEN admin sends PUT /productos/{id}/categorias with 2 categories
        THEN all existing categories are replaced and 200 is returned
        """
        admin, token = self._create_admin(session)

        cat1 = create_categoria(session, nombre="Cat1")
        cat2 = create_categoria(session, nombre="Cat2")

        producto = self._create_product_via_api(
            client, session, token, categoria_id=cat1.id,
        )

        payload = [
            {"categoria_id": cat1.id, "es_principal": False},
            {"categoria_id": cat2.id, "es_principal": True},
        ]
        resp = client.put(
            f"/api/v1/productos/{producto['id']}/categorias",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        cat_ids = [item["categoria_id"] for item in data]
        assert cat1.id in cat_ids
        assert cat2.id in cat_ids

    # ------------------------------------------------------------------
    # 4.3 — PUT con array vacío elimina todas las relaciones
    # ------------------------------------------------------------------

    def test_put_ingredientes_vacio_elimina_todos(
        self, session, client
    ):
        """
        WHEN admin sends PUT /productos/{id}/ingredientes with []
        THEN all ingredients are removed and 200 is returned with empty list
        """
        admin, token = self._create_admin(session)
        cat = create_categoria(session)
        ing = create_ingrediente(session)
        producto = self._create_product_via_api(client, session, token, ingrediente_id=ing.id, categoria_id=cat.id)

        resp = client.put(
            f"/api/v1/productos/{producto['id']}/ingredientes",
            json=[],
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        assert resp.json() == []

    def test_put_categorias_vacio_elimina_todas(
        self, session, client
    ):
        """
        WHEN admin sends PUT /productos/{id}/categorias with []
        THEN all categories are removed and 200 is returned with empty list
        """
        admin, token = self._create_admin(session)
        cat = create_categoria(session)
        ing = create_ingrediente(session)
        producto = self._create_product_via_api(client, session, token, ingrediente_id=ing.id, categoria_id=cat.id)

        resp = client.put(
            f"/api/v1/productos/{producto['id']}/categorias",
            json=[],
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        assert resp.json() == []

    # ------------------------------------------------------------------
    # 4.4 — PUT sobre producto inexistente devuelve 404
    # ------------------------------------------------------------------

    def test_put_ingredientes_producto_inexistente_404(
        self, session, client
    ):
        """
        WHEN admin sends PUT /productos/99999/ingredientes
        THEN return 404
        """
        admin, token = self._create_admin(session)
        resp = client.put(
            "/api/v1/productos/99999/ingredientes",
            json=[],
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

    def test_put_categorias_producto_inexistente_404(
        self, session, client
    ):
        """
        WHEN admin sends PUT /productos/99999/categorias
        THEN return 404
        """
        admin, token = self._create_admin(session)
        resp = client.put(
            "/api/v1/productos/99999/categorias",
            json=[],
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

    # ------------------------------------------------------------------
    # 4.5 — GET ingredientes lista relaciones
    # ------------------------------------------------------------------

    def test_get_ingredientes_lista_relaciones(
        self, session, client
    ):
        """
        WHEN client sends GET /productos/{id}/ingredientes
        THEN return all ingredient relationships (public endpoint)
        """
        admin, token = self._create_admin(session)
        ing = create_ingrediente(session, nombre="Queso")
        cat = create_categoria(session, nombre="Pizzas")
        producto = self._create_product_via_api(
            client, session, token, nombre="Pizza Get Ing",
            ingrediente_id=ing.id, categoria_id=cat.id,
        )

        resp = client.get(f"/api/v1/productos/{producto['id']}/ingredientes")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["ingrediente_id"] == ing.id
        assert data[0]["ingrediente_nombre"] == "Queso"

    # ------------------------------------------------------------------
    # 4.6 — GET categorías lista relaciones
    # ------------------------------------------------------------------

    def test_get_categorias_lista_relaciones(
        self, session, client
    ):
        """
        WHEN client sends GET /productos/{id}/categorias
        THEN return all category relationships (public endpoint)
        """
        admin, token = self._create_admin(session)
        cat = create_categoria(session, nombre="Bebidas")
        ing = create_ingrediente(session)
        producto = self._create_product_via_api(
            client, session, token, nombre="Pizza Get Cat",
            ingrediente_id=ing.id, categoria_id=cat.id,
        )

        resp = client.get(f"/api/v1/productos/{producto['id']}/categorias")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["categoria_id"] == cat.id
        assert data[0]["categoria_nombre"] == "Bebidas"

    # ------------------------------------------------------------------
    # 4.7 — POST agregar ingrediente funciona (después del bugfix)
    # ------------------------------------------------------------------

    def test_post_agregar_ingrediente(
        self, session, client
    ):
        """
        WHEN admin sends POST /productos/{id}/ingredientes with a valid ingredient
        THEN the ingredient is added and 200 is returned with the updated list
        """
        admin, token = self._create_admin(session)
        cat = create_categoria(session)
        ing1 = create_ingrediente(session, nombre="IngBase")
        producto = self._create_product_via_api(
            client, session, token, ingrediente_id=ing1.id, categoria_id=cat.id,
        )

        # Create another ingredient to add
        ing2 = create_ingrediente(session, nombre="Agregado")

        payload = {
            "ingrediente_id": ing2.id,
            "es_removible": True,
            "es_principal": False,
            "orden": 1,
        }
        resp = client.post(
            f"/api/v1/productos/{producto['id']}/ingredientes",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        data = resp.json()
        ing_ids = [item["ingrediente_id"] for item in data]
        assert ing2.id in ing_ids

    # ------------------------------------------------------------------
    # 4.8 — POST agregar categoría funciona (después del bugfix)
    # ------------------------------------------------------------------

    def test_post_agregar_categoria(
        self, session, client
    ):
        """
        WHEN admin sends POST /productos/{id}/categorias with a valid category
        THEN the category is added and 200 is returned with the updated list
        """
        admin, token = self._create_admin(session)
        cat1 = create_categoria(session, nombre="CatBase")
        ing = create_ingrediente(session)
        producto = self._create_product_via_api(
            client, session, token, ingrediente_id=ing.id, categoria_id=cat1.id,
        )

        cat2 = create_categoria(session, nombre="Agregada")

        payload = {
            "categoria_id": cat2.id,
            "es_principal": False,
        }
        resp = client.post(
            f"/api/v1/productos/{producto['id']}/categorias",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        data = resp.json()
        cat_ids = [item["categoria_id"] for item in data]
        assert cat2.id in cat_ids

    # ------------------------------------------------------------------
    # 4.9 — DELETE ingrediente funciona
    # ------------------------------------------------------------------

    def test_delete_ingrediente(
        self, session, client
    ):
        """
        WHEN admin sends DELETE /productos/{id}/ingredientes/{ing_id}
        THEN the relationship is removed and 204 is returned
        """
        admin, token = self._create_admin(session)
        cat = create_categoria(session)
        ing = create_ingrediente(session)
        producto = self._create_product_via_api(
            client, session, token, ingrediente_id=ing.id, categoria_id=cat.id,
        )

        resp = client.delete(
            f"/api/v1/productos/{producto['id']}/ingredientes/{ing.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 204

    # ------------------------------------------------------------------
    # 4.10 — DELETE categoría funciona
    # ------------------------------------------------------------------

    def test_delete_categoria(
        self, session, client
    ):
        """
        WHEN admin sends DELETE /productos/{id}/categorias/{cat_id}
        THEN the relationship is removed and 204 is returned
        """
        admin, token = self._create_admin(session)
        cat = create_categoria(session)
        ing = create_ingrediente(session)
        producto = self._create_product_via_api(
            client, session, token, ingrediente_id=ing.id, categoria_id=cat.id,
        )

        resp = client.delete(
            f"/api/v1/productos/{producto['id']}/categorias/{cat.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 204

    # ------------------------------------------------------------------
    # 4.11 — Duplicate category → 409 (unique constraint)
    # ------------------------------------------------------------------

    def test_duplicate_categoria_returns_409(
        self, session, client
    ):
        """
        WHEN admin tries to add the same category twice
        THEN return 409 Conflict
        """
        admin, token = self._create_admin(session)
        cat = create_categoria(session, nombre="Unica")
        ing = create_ingrediente(session)
        producto = self._create_product_via_api(
            client, session, token, ingrediente_id=ing.id, categoria_id=cat.id,
        )

        # Try to add the same category again
        payload = {
            "categoria_id": cat.id,
            "es_principal": False,
        }
        resp = client.post(
            f"/api/v1/productos/{producto['id']}/categorias",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 409

    def test_duplicate_ingrediente_returns_409(
        self, session, client
    ):
        """
        WHEN admin tries to add the same ingredient twice
        THEN return 409 Conflict
        """
        admin, token = self._create_admin(session)
        cat = create_categoria(session)
        ing = create_ingrediente(session, nombre="Unico")
        producto = self._create_product_via_api(
            client, session, token, ingrediente_id=ing.id, categoria_id=cat.id,
        )

        # Try to add the same ingredient again
        payload = {
            "ingrediente_id": ing.id,
            "es_removible": True,
            "es_principal": False,
            "orden": 0,
        }
        resp = client.post(
            f"/api/v1/productos/{producto['id']}/ingredientes",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 409


# ===================================================================
# Tests for Public Catalog Endpoints
# ===================================================================


class TestCatalogoPublico:
    """Tests for GET /api/v1/catalogo/productos and related endpoints."""

    def _create_admin_token(self, session):
        """Helper: create an admin user and return token."""
        admin = create_user(session, rol_id=Role.ADMIN.value)
        return create_token_for(admin)

    def _create_product_with_ingredients(
        self, session, client, token, nombre, disponible=True,
        ingredientes_data=None, categoria_id=None, stock_cantidad=10,
    ):
        """Helper: create a product via API with full associations."""
        if categoria_id is None:
            cat = create_categoria(session, nombre="Cat Catalogo")
            categoria_id = cat.id
        if ingredientes_data is None:
            ing = create_ingrediente(session, nombre="Ing Base", es_alergeno=False)
            ingredientes_data = [
                {
                    "ingrediente_id": ing.id,
                    "es_removible": True,
                    "es_principal": True,
                    "orden": 0,
                }
            ]

        payload = {
            "nombre": nombre,
            "descripcion": f"Descripción de {nombre}",
            "precio_base": 15.0,
            "stock_cantidad": stock_cantidad,
            "disponible": disponible,
            "tiempo_prep_min": 10,
            "categorias_ids": [categoria_id],
            "categoria_principal_id": categoria_id,
            "ingredientes": ingredientes_data,
        }
        resp = client.post(
            "/api/v1/productos/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        return resp.json()

    # ------------------------------------------------------------------
    # 5.1 — Catálogo público solo muestra disponibles para anónimos
    # ------------------------------------------------------------------

    def test_catalogo_solo_muestra_disponibles(self, session, client):
        """
        Scenario: Catálogo público solo muestra disponibles
        WHEN an anonymous user calls GET /api/v1/catalogo/productos
        THEN only products with disponible=True are returned
        """
        token = self._create_admin_token(session)

        # Create one available and one non-available product
        self._create_product_with_ingredients(
            session, client, token, nombre="Disponible", disponible=True,
        )
        self._create_product_with_ingredients(
            session, client, token, nombre="No Disponible", disponible=False,
        )

        response = client.get("/api/v1/catalogo/productos/")
        assert response.status_code == 200
        data = response.json()
        names = [item["nombre"] for item in data["items"]]
        assert "Disponible" in names
        assert "No Disponible" not in names

    # ------------------------------------------------------------------
    # 5.2 — Filtro excluir_alergenos funciona
    # ------------------------------------------------------------------

    def test_excluir_alergenos_filtra_correctamente(self, session, client):
        """
        Scenario: Filtro excluir_alergenos
        WHEN an anonymous user calls
            GET /api/v1/catalogo/productos?excluir_alergenos=<alergeno_id>
        THEN products containing that allergen are excluded
        """
        token = self._create_admin_token(session)

        # Create two ingredients: one alergeno, one not
        ing_alergeno = create_ingrediente(session, nombre="Alergeno Test", es_alergeno=True)
        ing_normal = create_ingrediente(session, nombre="Normal Test", es_alergeno=False)
        cat = create_categoria(session)

        # Product with the allergen
        prod_con_alergeno = self._create_product_with_ingredients(
            session, client, token,
            nombre="Con Alergeno",
            ingredientes_data=[
                {
                    "ingrediente_id": ing_alergeno.id,
                    "es_removible": True,
                    "es_principal": True,
                    "orden": 0,
                }
            ],
            categoria_id=cat.id,
        )

        # Product without the allergen
        prod_sin_alergeno = self._create_product_with_ingredients(
            session, client, token,
            nombre="Sin Alergeno",
            ingredientes_data=[
                {
                    "ingrediente_id": ing_normal.id,
                    "es_removible": True,
                    "es_principal": True,
                    "orden": 0,
                }
            ],
            categoria_id=cat.id,
        )

        # Filter excluding the allergen ingredient
        response = client.get(
            f"/api/v1/catalogo/productos/?excluir_alergenos={ing_alergeno.id}"
        )
        assert response.status_code == 200
        data = response.json()
        names = [item["nombre"] for item in data["items"]]
        assert "Sin Alergeno" in names
        assert "Con Alergeno" not in names

    # ------------------------------------------------------------------
    # 5.3 — Detalle expandido incluye ingredientes y categorías
    # ------------------------------------------------------------------

    def test_detalle_incluye_ingredientes_y_categorias(self, session, client):
        """
        Scenario: Detalle expandido incluye ingredientes y categorías
        WHEN an anonymous user calls GET /api/v1/catalogo/productos/{id}
        THEN the response includes ingredientes (with es_alergeno) and categorias
        """
        token = self._create_admin_token(session)
        cat = create_categoria(session, nombre="Pizzas")
        ing = create_ingrediente(session, nombre="Queso", es_alergeno=True)

        producto = self._create_product_with_ingredients(
            session, client, token,
            nombre="Pizza Catalogo",
            ingredientes_data=[
                {
                    "ingrediente_id": ing.id,
                    "es_removible": True,
                    "es_principal": True,
                    "orden": 0,
                }
            ],
            categoria_id=cat.id,
        )

        response = client.get(f"/api/v1/catalogo/productos/{producto['id']}")
        assert response.status_code == 200
        data = response.json()

        # Check ingredients
        assert len(data["ingredientes"]) == 1
        assert data["ingredientes"][0]["ingrediente_nombre"] == "Queso"
        assert data["ingredientes"][0]["es_alergeno"] is True

        # Check categories
        assert len(data["categorias"]) == 1
        assert data["categorias"][0]["categoria_nombre"] == "Pizzas"

    # ------------------------------------------------------------------
    # 5.4 — Detalle no expone stock_cantidad exacta
    # ------------------------------------------------------------------

    def test_detalle_no_expone_stock_cantidad(self, session, client):
        """
        Scenario: Detalle no expone stock_cantidad exacta
        WHEN an anonymous user calls GET /api/v1/catalogo/productos/{id}
        THEN the response includes hay_stock but NOT stock_cantidad
        """
        token = self._create_admin_token(session)
        cat = create_categoria(session)
        ing = create_ingrediente(session)

        producto = self._create_product_with_ingredients(
            session, client, token,
            nombre="Sin Stock Exacto",
            stock_cantidad=5,
            categoria_id=cat.id,
            ingredientes_data=[
                {
                    "ingrediente_id": ing.id,
                    "es_removible": True,
                    "es_principal": True,
                    "orden": 0,
                }
            ],
        )

        response = client.get(f"/api/v1/catalogo/productos/{producto['id']}")
        assert response.status_code == 200
        data = response.json()

        # Should have hay_stock = True (stock_cantidad=5 > 0)
        assert "hay_stock" in data
        assert data["hay_stock"] is True

        # Should NOT have stock_cantidad
        assert "stock_cantidad" not in data

        # Should NOT have eliminado_en
        assert "eliminado_en" not in data

    # ------------------------------------------------------------------
    # 5.5 — Paginación con page/limit devuelve conteo total
    # ------------------------------------------------------------------

    def test_paginacion_devuelve_total_count(self, session, client):
        """
        Scenario: Paginación con page/limit devuelve total_count
        WHEN an anonymous user calls
            GET /api/v1/catalogo/productos?page=1&limit=2
        THEN the response includes total_count with total matching products
        """
        token = self._create_admin_token(session)
        cat = create_categoria(session)
        ing = create_ingrediente(session)

        # Create 3 products
        for i in range(3):
            self._create_product_with_ingredients(
                session, client, token,
                nombre=f"Producto {i}",
                categoria_id=cat.id,
                ingredientes_data=[
                    {
                        "ingrediente_id": ing.id,
                        "es_removible": True,
                        "es_principal": True,
                        "orden": 0,
                    }
                ],
            )

        # Request page=1 with limit=2
        response = client.get("/api/v1/catalogo/productos/?page=1&limit=2")
        assert response.status_code == 200
        data = response.json()

        # Should have total_count = 3
        assert data["total_count"] == 3
        assert len(data["items"]) == 2

        # Page 2 should have 1 item
        response2 = client.get("/api/v1/catalogo/productos/?page=2&limit=2")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total_count"] == 3
        assert len(data2["items"]) == 1

    # ------------------------------------------------------------------
    # 5.6 — Producto no disponible da 404 en detalle público
    # ------------------------------------------------------------------

    def test_producto_no_disponible_da_404(self, session, client):
        """
        Scenario: Producto no disponible da 404 en detalle público
        WHEN an anonymous user calls GET /api/v1/catalogo/productos/{id}
            for a product with disponible=false
        THEN the system returns HTTP 404
        """
        token = self._create_admin_token(session)

        producto = self._create_product_with_ingredients(
            session, client, token,
            nombre="No Disponible",
            disponible=False,
        )

        response = client.get(f"/api/v1/catalogo/productos/{producto['id']}")
        assert response.status_code == 404

    def test_soft_deleted_producto_da_404_en_catalogo(self, session, client):
        """
        Scenario: Producto soft-deleted da 404 en detalle público
        WHEN an anonymous user calls GET /api/v1/catalogo/productos/{id}
            for a soft-deleted product
        THEN the system returns HTTP 404
        """
        admin_token = self._create_admin_token(session)

        producto = self._create_product_with_ingredients(
            session, client, admin_token,
            nombre="Será Eliminado",
            disponible=True,
        )

        # Soft delete via admin endpoint
        client.delete(
            f"/api/v1/productos/{producto['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # Try to access via catalog
        response = client.get(f"/api/v1/catalogo/productos/{producto['id']}")
        assert response.status_code == 404
