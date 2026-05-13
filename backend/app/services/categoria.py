# Categoria Service
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select

from fastapi import HTTPException, status

from app.models.categoria import Categoria
from app.core.repositories.categoria import CategoriaRepository
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaTree


class CategoriaService:
    """Service for Categoria operations following Router -> Service -> Repository pattern."""

    def __init__(self, session: Session, repo: Optional[CategoriaRepository] = None):
        self.session = session
        self.repo = repo or CategoriaRepository(session)

    def create(self, data: CategoriaCreate) -> Categoria:
        """Create a new category with business validations."""
        # Validate nombre is unique
        existing = self.repo.get_by_name(data.nombre)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )

        # Validate parent_id exists if provided
        if data.parent_id is not None:
            parent = self.repo.get(data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent category not found",
                )

        now = datetime.now(timezone.utc).isoformat()
        categoria = Categoria(
            nombre=data.nombre,
            descripcion=data.descripcion,
            parent_id=data.parent_id,
            orden_display=data.orden_display,
            fecha_creacion=now,
            fecha_actualizacion=now,
        )
        return self.repo.create(categoria)

    def get_tree(self, include_deleted: bool = False) -> list[CategoriaTree]:
        """Build and return the full category tree."""
        statement = select(Categoria)
        if not include_deleted:
            statement = statement.where(Categoria.eliminado_en.is_(None))
        statement = statement.order_by(Categoria.orden_display)
        categories = list(self.session.exec(statement))

        # Build flat dict of tree nodes
        cat_dict: dict[int, CategoriaTree] = {}
        for cat in categories:
            cat_dict[cat.id] = CategoriaTree(
                id=cat.id,
                nombre=cat.nombre,
                descripcion=cat.descripcion,
                parent_id=cat.parent_id,
                orden_display=cat.orden_display,
                subcategorias=[],
            )

        # Build tree structure by attaching children to parents
        roots: list[CategoriaTree] = []
        for cat in categories:
            tree_node = cat_dict[cat.id]
            if cat.parent_id is None:
                roots.append(tree_node)
            elif cat.parent_id in cat_dict:
                cat_dict[cat.parent_id].subcategorias.append(tree_node)

        return roots

    def get_by_id(self, categoria_id: int) -> Categoria:
        """Get a single category by ID (excludes soft-deleted)."""
        categoria = self.repo.get(categoria_id)
        if not categoria or categoria.eliminado_en is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        return categoria

    def update(self, categoria_id: int, data: CategoriaUpdate) -> Categoria:
        """Update a category with validations (unique name, no cycles)."""
        categoria = self.repo.get(categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        update_data = data.model_dump(exclude_unset=True)

        # Validate nombre uniqueness if being changed
        if "nombre" in update_data:
            existing = self.repo.get_by_name(update_data["nombre"])
            if existing and existing.id != categoria_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category name already exists",
                )

        # Validate parent_id changes
        if "parent_id" in update_data:
            new_parent_id = update_data["parent_id"]
            if new_parent_id is not None:
                # Cannot set parent to self
                if new_parent_id == categoria_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot set category as its own parent",
                    )
                # Validate parent exists
                parent = self.repo.get(new_parent_id)
                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Parent category not found",
                    )
                # Cannot create circular reference
                if self._check_cycle(categoria_id, new_parent_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot create circular reference",
                    )

        update_data["fecha_actualizacion"] = datetime.now(timezone.utc).isoformat()

        updated = self.repo.update(categoria_id, update_data)
        self.session.refresh(updated)
        return updated

    def soft_delete(self, categoria_id: int) -> Categoria:
        """Soft delete a category by setting eliminado_en timestamp."""
        categoria = self.repo.get(categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        now = datetime.now(timezone.utc).isoformat()
        updated = self.repo.update(categoria_id, {
            "eliminado_en": now,
            "fecha_actualizacion": now,
        })
        self.session.refresh(updated)
        return updated

    def _check_cycle(self, categoria_id: int, new_parent_id: int) -> bool:
        """
        Check if setting new_parent_id as parent of categoria_id creates a cycle.
        Walks up the tree from new_parent_id toward root.
        """
        current_id = new_parent_id
        while current_id is not None:
            if current_id == categoria_id:
                return True
            parent = self.repo.get(current_id)
            if parent is None:
                break
            current_id = parent.parent_id
        return False
