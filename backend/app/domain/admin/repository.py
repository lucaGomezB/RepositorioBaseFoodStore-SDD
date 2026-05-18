# Configuracion Repository
from typing import List, Optional
from sqlmodel import Session, select
from app.models.configuracion import Configuracion


class ConfiguracionRepository:
    """Repository for system configuration operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Configuracion]:
        """Get all configurations."""
        statement = select(Configuracion).order_by(Configuracion.clave)
        return list(self.session.exec(statement))

    def get_by_clave(self, clave: str) -> Optional[Configuracion]:
        """Get a configuration by key."""
        return self.session.get(Configuracion, clave)

    def upsert(self, conf: Configuracion) -> Configuracion:
        """Insert or update a configuration."""
        self.session.add(conf)
        return conf
