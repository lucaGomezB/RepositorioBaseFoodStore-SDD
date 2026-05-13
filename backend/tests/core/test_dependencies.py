# Integration tests for dependency injection patterns
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_db,
    create_repository,
    get_usuario_repo,
    get_rol_repo,
    get_estado_pedido_repo,
    get_forma_pago_repo,
    get_uow,
)


class TestGetDb:
    """Tests for the get_db dependency."""

    def test_get_db_yields_session(self):
        """Test that get_db yields a session."""
        # Create a mock session
        mock_session = MagicMock(spec=Session)
        
        # Patch SessionLocal to return our mock session
        with patch("app.core.database.SessionLocal") as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Call get_db and iterate
            result = list(get_db())
            
            assert len(result) == 1
            assert result[0] is mock_session

    def test_get_db_closes_session(self):
        """Test that session is closed after use."""
        mock_session = MagicMock()
        
        with patch("app.core.database.SessionLocal") as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # Consume the generator
            list(get_db())
            
            # Verify close was called
            mock_session.close.assert_called_once()


class TestCreateRepository:
    """Tests for the repository factory."""

    def test_create_repository_returns_base_repository(self, session):
        """Test that factory returns a BaseRepository."""
        from app.models.usuario import Usuario
        from app.core.repositories.base import BaseRepository
        
        repo = create_repository(Usuario, session)
        
        assert isinstance(repo, BaseRepository)
        assert repo.model == Usuario

    def test_create_repository_uses_provided_session(self, session):
        """Test that repository uses the provided session."""
        from app.models.usuario import Usuario
        
        repo = create_repository(Usuario, session)
        
        assert repo.session is session


class TestSpecificDependencies:
    """Tests for specific model dependencies."""

    def test_get_usuario_repo(self, session):
        """Test get_usuario_repo returns correct repository."""
        from app.models.usuario import Usuario
        
        with patch("app.core.dependencies.get_db") as mock_get_db:
            mock_get_db.return_value = iter([session])
            
            repo = get_usuario_repo(session)
            
            assert repo.model == Usuario
            assert repo.session is session

    def test_get_rol_repo(self, session):
        """Test get_rol_repo returns correct repository."""
        from app.models.rol import Rol
        
        with patch("app.core.dependencies.get_db") as mock_get_db:
            mock_get_db.return_value = iter([session])
            
            repo = get_rol_repo(session)
            
            assert repo.model == Rol

    def test_get_estado_pedido_repo(self, session):
        """Test get_estado_pedido_repo returns correct repository."""
        from app.models.estado_pedido import EstadoPedido
        
        with patch("app.core.dependencies.get_db") as mock_get_db:
            mock_get_db.return_value = iter([session])
            
            repo = get_estado_pedido_repo(session)
            
            assert repo.model == EstadoPedido

    def test_get_forma_pago_repo(self, session):
        """Test get_forma_pago_repo returns correct repository."""
        from app.models.forma_pago import FormaPago
        
        with patch("app.core.dependencies.get_db") as mock_get_db:
            mock_get_db.return_value = iter([session])
            
            repo = get_forma_pago_repo(session)
            
            assert repo.model == FormaPago


class TestGetUow:
    """Tests for the Unit of Work dependency."""

    def test_get_uow_returns_unit_of_work(self, session):
        """Test that get_uow returns a UnitOfWork instance."""
        from app.core.uow import UnitOfWork
        
        with patch("app.core.dependencies.get_db") as mock_get_db:
            mock_get_db.return_value = iter([session])
            
            uow = get_uow(session)
            
            assert isinstance(uow, UnitOfWork)
            assert uow.session is session

    def test_get_uow_can_register_repositories(self, session):
        """Test that UoW from dependency can register repositories."""
        from app.models.usuario import Usuario
        
        with patch("app.core.dependencies.get_db") as mock_get_db:
            mock_get_db.return_value = iter([session])
            
            uow = get_uow(session)
            repo = uow.register(Usuario, "usuario")
            
            assert repo.model == Usuario