# Categoria Repository
from app.core.repositories.base import BaseRepository
from app.models.categoria import Categoria


class CategoriaRepository(BaseRepository[Categoria]):
    """Repository for Categoria model."""
    
    def __init__(self, session):
        super().__init__(Categoria, session)
    
    def get_by_name(self, nombre: str) -> Categoria:
        """Get category by name."""
        return self.get_by_field("nombre", nombre)
    
    def get_children(self, parent_id: int) -> list[Categoria]:
        """Get child categories."""
        return self.get_multi_by_field("parent_id", parent_id)
    
    def get_root_categories(self) -> list[Categoria]:
        """Get categories with no parent (root categories)."""
        from sqlmodel import select
        statement = select(Categoria).where(Categoria.parent_id.is_(None))
        return list(self.session.exec(statement))