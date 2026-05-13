# pytest configuration and fixtures for backend tests
import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from app.models.usuario import Usuario


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
        yield session


@pytest.fixture
def test_user(session: Session) -> Usuario:
    """Create a test user in the database."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    user = Usuario(
        email="test@example.com",
        password_hash="hashedpassword",
        nombre="Test",
        apellido="User",
        rol_id=1,
        activo=True,
        fecha_creacion=now,
        fecha_actualizacion=now
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user