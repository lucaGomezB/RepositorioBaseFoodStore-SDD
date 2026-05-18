# Repository module — only BaseRepository remains in core
# All domain repositories moved to app.domain.*
from app.core.repositories.base import BaseRepository

__all__ = [
    "BaseRepository",
]
