# pytest configuration and fixtures for backend tests
import pytest
from sqlmodel import SQLModel, Session, select, create_engine
from sqlalchemy.pool import StaticPool
from app.models.usuario import Usuario


def seed_roles(session: Session) -> None:
    """Seed the roles table if empty (idempotent)."""
    from app.models.rol import Rol
    existing = session.exec(select(Rol).limit(1)).first()
    if not existing:
        roles = [
            Rol(id=1, nombre="ADMIN", descripcion="Administrator"),
            Rol(id=2, nombre="STOCK", descripcion="Stock Manager"),
            Rol(id=3, nombre="PEDIDOS", descripcion="Orders Manager"),
            Rol(id=4, nombre="CLIENT", descripcion="Client"),
        ]
        for r in roles:
            session.add(r)
        session.flush()


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
    """Create a new session for each test."""
    with Session(engine) as session:
        seed_roles(session)
        session.commit()
        yield session


@pytest.fixture
def test_user(session: Session) -> Usuario:
    """Create a test user in the database."""
    from datetime import datetime, timezone
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