# Admin Configuration endpoints integration tests
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
from app.models.configuracion import Configuracion
from app.core.database import get_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
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
    with Session(engine) as s:
        yield s


@pytest.fixture
def client(session: Session):
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


def create_admin(session: Session) -> Usuario:
    now = datetime.now(timezone.utc).isoformat()
    user = Usuario(
        email="admin@test.com",
        password_hash="hashed",
        nombre="Admin",
        apellido="Test",
        rol_id=Role.ADMIN.value,
        activo=True,
        fecha_creacion=now,
        fecha_actualizacion=now,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_token_for(user: Usuario) -> str:
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "rol_id": user.rol_id,
        "nonce": time.time(),
    }
    return create_access_token(token_data)


def seed_configs(session: Session):
    configs = [
        Configuracion(clave="costo_envio", valor="50.00", descripcion="Costo de envío", updated_at=datetime.now(timezone.utc)),
        Configuracion(clave="horario_apertura", valor="09:00", descripcion="Apertura", updated_at=datetime.now(timezone.utc)),
    ]
    for c in configs:
        session.add(c)
    session.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestConfigList:
    def test_listar_configuraciones(self, client, session):
        """6.1 GET /admin/configuracion retorna lista."""
        admin = create_admin(session)
        token = create_token_for(admin)
        seed_configs(session)

        response = client.get(
            "/api/v1/admin/configuracion",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2


class TestConfigUpdate:
    def test_actualizar_configuracion(self, client, session):
        """6.2 PUT /admin/configuracion actualiza valores."""
        admin = create_admin(session)
        token = create_token_for(admin)
        seed_configs(session)

        response = client.put(
            "/api/v1/admin/configuracion",
            json={
                "configuraciones": [
                    {"clave": "costo_envio", "valor": "75.00"},
                ]
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # Verify the update
        costo = next((c for c in data if c["clave"] == "costo_envio"), None)
        assert costo is not None
        assert costo["valor"] == "75.00"

    def test_actualizar_clave_invalida(self, client, session):
        """6.3 PUT con clave inválida retorna 400."""
        admin = create_admin(session)
        token = create_token_for(admin)
        seed_configs(session)

        response = client.put(
            "/api/v1/admin/configuracion",
            json={
                "configuraciones": [
                    {"clave": "clave_inexistente", "valor": "abc"},
                ]
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        assert "no encontrada" in response.json()["detail"].lower()
