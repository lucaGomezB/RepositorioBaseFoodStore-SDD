# BaseRepository[T] - Generic repository with CRUD operations
from typing import Generic, TypeVar, Type, List, Optional, Any, Dict
from sqlmodel import Session, SQLModel, select
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """
    Generic base repository with standard CRUD operations.
    Subclass this for specific models:
    
    Example:
        class UsuarioRepository(BaseRepository[Usuario]):
            pass
    """

    def __init__(self, model: Type[T], session: Session):
        self._model = model
        self.session = session

    @property
    def model(self) -> Type[T]:
        """Get the model class."""
        return self._model

    def create(self, obj: T) -> T:
        """
        Create a new record in the database.
        
        Args:
            obj: SQLModel instance to create
            
        Returns:
            The created instance with id populated
        """
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get(self, id: int) -> Optional[T]:
        """
        Get a single record by primary key.
        
        Args:
            id: Primary key value
            
        Returns:
            The instance if found, None otherwise
        """
        return self.session.get(self._model, id)

    def get_all(self) -> List[T]:
        """
        Get all records of this model.
        
        Returns:
            List of all instances
        """
        statement = select(self._model)
        return list(self.session.exec(statement))

    def update(self, id: int, updates: Dict[str, Any]) -> Optional[T]:
        """
        Update a record by ID with given updates.
        
        Args:
            id: Primary key value
            updates: Dictionary of field names to new values
            
        Returns:
            The updated instance if found, None otherwise
        """
        obj = self.get(id)
        if obj is None:
            return None

        for key, value in updates.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: Primary key value
            
        Returns:
            True if deleted, False if not found
        """
        obj = self.get(id)
        if obj is None:
            return False

        self.session.delete(obj)
        self.session.commit()
        return True

    def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """
        Get a single record by any field.
        
        Args:
            field: Name of the field to query
            value: Value to match
            
        Returns:
            The first matching instance, None if not found
        """
        if not hasattr(self._model, field):
            raise ValueError(f"Model {self._model.__name__} has no field '{field}'")

        statement = select(self._model).where(getattr(self._model, field) == value)
        return self.session.exec(statement).first()

    def get_multi_by_field(self, field: str, value: Any) -> List[T]:
        """
        Get all records matching a field value.
        
        Args:
            field: Name of the field to query
            value: Value to match
            
        Returns:
            List of matching instances
        """
        if not hasattr(self._model, field):
            raise ValueError(f"Model {self._model.__name__} has no field '{field}'")

        statement = select(self._model).where(getattr(self._model, field) == value)
        return list(self.session.exec(statement))

    def count(self) -> int:
        """
        Count total records in the table.
        
        Returns:
            Number of records
        """
        statement = select(self._model)
        return len(list(self.session.exec(statement)))