# Tests for UnitOfWork
from datetime import datetime, timezone
from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.core.repositories.base import BaseRepository
from app.models.usuario import Usuario


def make_user(**kwargs) -> Usuario:
    """Helper to create user with defaults."""
    now = datetime.now(timezone.utc).isoformat()
    defaults = {
        "email": "default@example.com",
        "password_hash": "hash",
        "nombre": "Default",
        "apellido": "User",
        "activo": True,
        "fecha_creacion": now,
        "fecha_actualizacion": now,
    }
    defaults.update(kwargs)
    return Usuario(**defaults)


class TestUnitOfWork:
    """Tests for the UnitOfWork class."""

    def test_context_manager_commits_on_exit(self, session: Session):
        """Test that changes are committed when exiting normally."""
        with UnitOfWork(session) as uow:
            user = make_user(email="commit@test.com", nombre="Commit")
            uow.session.add(user)
        
        # Verify user was committed
        found = session.get(Usuario, user.id)
        assert found is not None
        assert found.email == "commit@test.com"

    def test_context_manager_rolls_back_on_exception(self, session: Session):
        """Test that changes are rolled back when exception occurs."""
        try:
            with UnitOfWork(session) as uow:
                user = make_user(email="rollback@test.com", nombre="Rollback")
                uow.session.add(user)
                raise ValueError("Simulated error")
        except ValueError:
            pass
        
        # Verify user was NOT committed
        from sqlmodel import select
        statement = select(Usuario).where(Usuario.email == "rollback@test.com")
        result = session.exec(statement).first()
        assert result is None

    def test_register_repository(self, session: Session):
        """Test registering a repository."""
        with UnitOfWork(session) as uow:
            usuario_repo = uow.register(Usuario, "usuario")
            
            assert isinstance(usuario_repo, BaseRepository)
            assert usuario_repo.model == Usuario

    def test_access_repository_via_attribute(self, session: Session):
        """Test accessing repository via attribute."""
        with UnitOfWork(session) as uow:
            uow.register(Usuario, "usuario")
            
            # Should be accessible via attribute
            assert hasattr(uow, "usuario")
            assert isinstance(uow.usuario, BaseRepository)

    def test_get_repo_by_name(self, session: Session):
        """Test getting repository by name."""
        with UnitOfWork(session) as uow:
            uow.register(Usuario, "custom_name")
            
            repo = uow.get_repo("custom_name")
            assert repo is not None
            assert isinstance(repo, BaseRepository)

    def test_get_repo_not_found(self, session: Session):
        """Test getting non-existent repository returns None."""
        with UnitOfWork(session) as uow:
            repo = uow.get_repo("nonexistent")
            assert repo is None

    def test_manual_commit(self, session: Session):
        """Test manual commit method."""
        with UnitOfWork(session) as uow:
            user = make_user(email="manual@test.com", nombre="Manual")
            uow.session.add(user)
            uow.commit()
        
        found = session.get(Usuario, user.id)
        assert found is not None

    def test_manual_rollback(self, session: Session):
        """Test manual rollback method."""
        with UnitOfWork(session) as uow:
            user = make_user(email="before@test.com", nombre="Before")
            uow.session.add(user)
            uow.rollback()
        
        # After rollback, user should not be committed
        from sqlmodel import select
        statement = select(Usuario).where(Usuario.email == "before@test.com")
        result = session.exec(statement).first()
        assert result is None