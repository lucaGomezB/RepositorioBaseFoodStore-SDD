# Ingrediente Repository
from app.core.repositories.base import BaseRepository
from app.models.ingrediente import Ingrediente


class IngredienteRepository(BaseRepository[Ingrediente]):
    """Repository for Ingrediente model."""
    
    def __init__(self, session):
        super().__init__(Ingrediente, session)
    
    def get_by_name(self, nombre: str) -> Ingrediente:
        """Get ingredient by name."""
        return self.get_by_field("nombre", nombre)
