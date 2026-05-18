# Unit of Work pattern for transaction management
from typing import Dict, Type, Optional
from sqlmodel import Session, SQLModel
from app.core.repositories.base import BaseRepository


class UnitOfWork:
    """
    Unit of Work pattern for managing database transactions.
    
    Usage:
        with UnitOfWork(session) as uow:
            uow.usuario_repo = UsuarioRepository(Usuario, uow.session)
            user = uow.usuario_repo.get(1)
            # Changes committed automatically on successful exit
    """

    def __init__(self, session: Session):
        self._session = session
        self._repositories: Dict[str, BaseRepository] = {}

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            # Exception occurred - rollback
            self._session.rollback()
            return False  # Don't suppress the exception
        
        # No exception - commit
        self._session.commit()
        return False

    @property
    def session(self) -> Session:
        """Get the database session."""
        return self._session

    def register(self, model: Type[SQLModel], name: Optional[str] = None) -> BaseRepository:
        """
        Register and create a repository for a model.
        
        Args:
            model: SQLModel subclass
            name: Optional name for the repository (defaults to model name)
            
        Returns:
            New BaseRepository instance for the model
        """
        repo_name = name or model.__name__.lower()
        repo = BaseRepository(model, self._session)
        self._repositories[repo_name] = repo
        return repo

    def get_repo(self, name: str) -> Optional[BaseRepository]:
        """
        Get a registered repository by name.
        
        Args:
            name: Repository name
            
        Returns:
            The repository if found, None otherwise
        """
        return self._repositories.get(name)

    def __getattr__(self, name: str) -> BaseRepository:
        """
        Allow attribute access to repositories: uow.usuario_repo
        """
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
        if name in self._repositories:
            return self._repositories[name]
        
        raise AttributeError(
            f"'{type(self).__name__}' has no repository '{name}'. "
            f"Use register() to add repositories or check registered: {list(self._repositories.keys())}"
        )

    def commit(self) -> None:
        """Manually commit the current transaction."""
        self._session.commit()

    def rollback(self) -> None:
        """Manually rollback the current transaction."""
        self._session.rollback()