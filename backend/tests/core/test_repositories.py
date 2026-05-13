# Tests for BaseRepository
import pytest
from datetime import datetime
from app.core.repositories.base import BaseRepository
from app.models.usuario import Usuario


def make_user(**kwargs) -> Usuario:
    """Helper to create user with defaults."""
    now = datetime.utcnow().isoformat()
    defaults = {
        "email": "default@example.com",
        "password_hash": "hash",
        "nombre": "Default",
        "apellido": "User",
        "rol_id": 1,
        "activo": True,
        "fecha_creacion": now,
        "fecha_actualizacion": now,
    }
    defaults.update(kwargs)
    return Usuario(**defaults)


class TestBaseRepository:
    """Tests for the BaseRepository generic class."""

    def test_create(self, session, test_user):
        """Test creating a new record."""
        repo = BaseRepository(Usuario, session)

        new_user = make_user(email="new@example.com", nombre="New")
        created = repo.create(new_user)

        assert created.id is not None
        assert created.email == "new@example.com"
        assert created.nombre == "New"

    def test_get(self, session, test_user):
        """Test getting a record by ID."""
        repo = BaseRepository(Usuario, session)

        found = repo.get(test_user.id)

        assert found is not None
        assert found.id == test_user.id
        assert found.email == test_user.email

    def test_get_not_found(self, session, test_user):
        """Test getting a non-existent record returns None."""
        repo = BaseRepository(Usuario, session)

        found = repo.get(9999)

        assert found is None

    def test_get_all(self, session, test_user):
        """Test getting all records."""
        repo = BaseRepository(Usuario, session)

        # Add another user
        user2 = make_user(email="another@example.com", nombre="Another")
        repo.create(user2)

        all_users = repo.get_all()

        assert len(all_users) >= 2

    def test_update(self, session, test_user):
        """Test updating a record."""
        repo = BaseRepository(Usuario, session)

        updated = repo.update(test_user.id, {"nombre": "UpdatedName"})

        assert updated is not None
        assert updated.nombre == "UpdatedName"

    def test_update_not_found(self, session, test_user):
        """Test updating non-existent record returns None."""
        repo = BaseRepository(Usuario, session)

        result = repo.update(9999, {"nombre": "Updated"})

        assert result is None

    def test_delete(self, session, test_user):
        """Test deleting a record."""
        repo = BaseRepository(Usuario, session)

        deleted = repo.delete(test_user.id)

        assert deleted is True

        # Verify it's gone
        found = repo.get(test_user.id)
        assert found is None

    def test_delete_not_found(self, session, test_user):
        """Test deleting non-existent record returns False."""
        repo = BaseRepository(Usuario, session)

        result = repo.delete(9999)

        assert result is False

    def test_get_by_field(self, session, test_user):
        """Test getting a record by any field."""
        repo = BaseRepository(Usuario, session)

        found = repo.get_by_field("email", "test@example.com")

        assert found is not None
        assert found.id == test_user.id

    def test_count(self, session, test_user):
        """Test counting records."""
        repo = BaseRepository(Usuario, session)

        count = repo.count()

        assert count >= 1