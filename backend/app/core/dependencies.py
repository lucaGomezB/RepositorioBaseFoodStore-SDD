# FastAPI dependency injection patterns
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

# Import get_db from existing database module
from app.core.database import get_db as get_db_session


# Re-export get_db for convenience - this uses the existing implementation
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Yields a session and ensures it's closed after the request.
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    yield from get_db_session()


# Type alias for clarity
DatabaseSession = Session


# Repository factory - can be extended as new models are added
def create_repository(model_class: type, session: Session):
    """
    Factory function to create a repository for any model.
    
    Args:
        model_class: SQLModel subclass (e.g., Usuario, Producto)
        session: Database session
        
    Returns:
        BaseRepository instance for the model
    """
    from app.core.repositories.base import BaseRepository
    return BaseRepository(model_class, session)


# Import models to use with repository factory
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago

# Import other models if they exist (will fail gracefully if not created yet)
try:
    from app.models.producto import Producto
    _has_producto = True
except ImportError:
    _has_producto = False

try:
    from app.models.categoria import Categoria
    _has_categoria = True
except ImportError:
    _has_categoria = False

try:
    from app.models.pedido import Pedido
    _has_pedido = True
except ImportError:
    _has_pedido = False

try:
    from app.models.direccion import Direccion
    _has_direccion = True
except ImportError:
    _has_direccion = False


# Specific repository dependencies
def get_usuario_repo(db: Session = Depends(get_db)):
    """Get Usuario repository."""
    return create_repository(Usuario, db)


def get_rol_repo(db: Session = Depends(get_db)):
    """Get Rol repository."""
    return create_repository(Rol, db)


def get_estado_pedido_repo(db: Session = Depends(get_db)):
    """Get EstadoPedido repository."""
    return create_repository(EstadoPedido, db)


def get_forma_pago_repo(db: Session = Depends(get_db)):
    """Get FormaPago repository."""
    return create_repository(FormaPago, db)


# Conditional dependencies for models that may not exist yet
def get_producto_repo(db: Session = Depends(get_db)):
    """Get Producto repository."""
    if not _has_producto:
        raise NotImplementedError("Producto model not yet created")
    return create_repository(Producto, db)


def get_categoria_repo(db: Session = Depends(get_db)):
    """Get Categoria repository."""
    if not _has_categoria:
        raise NotImplementedError("Categoria model not yet created")
    return create_repository(Categoria, db)


def get_pedido_repo(db: Session = Depends(get_db)):
    """Get Pedido repository."""
    if not _has_pedido:
        raise NotImplementedError("Pedido model not yet created")
    return create_repository(Pedido, db)


def get_direccion_repo(db: Session = Depends(get_db)):
    """Get Direccion repository."""
    if not _has_direccion:
        raise NotImplementedError("Direccion model not yet created")
    return create_repository(Direccion, db)


# Unit of Work dependency
def get_uow(db: Session = Depends(get_db)):
    """
    Get a UnitOfWork instance for transaction management.
    
    Usage:
        @app.post("/orders")
        def create_order(uow = Depends(get_uow)):
            with uow:
                uow.pedido_repo.create(order)
                # Automatically commits on success, rolls back on exception
    """
    from app.core.uow import UnitOfWork
    return UnitOfWork(db)


__all__ = [
    "get_db",
    "create_repository",
    "get_usuario_repo",
    "get_rol_repo",
    "get_estado_pedido_repo",
    "get_forma_pago_repo",
    "get_producto_repo",
    "get_categoria_repo",
    "get_pedido_repo",
    "get_direccion_repo",
    "get_uow",
    "DatabaseSession",
    # Re-export for convenience
    "get_db as DatabaseDependency",
]