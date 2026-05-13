"""add unique constraints to link tables

Revision ID: e1f2a3b4c5d6
Revises: a1b2c3d4e5f6
Create Date: 2026-05-12 18:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add unique constraint on producto_categoria (producto_id, categoria_id)
    op.create_unique_constraint(
        "uq_producto_categoria",
        "producto_categoria",
        ["producto_id", "categoria_id"],
    )
    # Add unique constraint on producto_ingrediente (producto_id, ingrediente_id)
    op.create_unique_constraint(
        "uq_producto_ingrediente",
        "producto_ingrediente",
        ["producto_id", "ingrediente_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_producto_ingrediente", "producto_ingrediente", type_="unique")
    op.drop_constraint("uq_producto_categoria", "producto_categoria", type_="unique")
