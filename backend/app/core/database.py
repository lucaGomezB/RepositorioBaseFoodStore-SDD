# SQLAlchemy database configuration and session management
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session
from typing import Generator
from app.core.config import settings

# Create engine with DATABASE_URL from settings
engine = create_engine(
    settings.DATABASE_URL,
    echo=(settings.LOG_LEVEL == "DEBUG"),
    pool_pre_ping=True,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    Yields a session and ensures it's closed after the request.
    Commits on success, rolls back on error.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()