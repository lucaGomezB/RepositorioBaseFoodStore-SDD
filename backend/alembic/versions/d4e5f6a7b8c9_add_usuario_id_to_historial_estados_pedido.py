"""add usuario_id to historial_estados_pedido

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-12 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add usuario_id column to historial_estados_pedido."""
    op.add_column(
        "historial_estados_pedido",
        sa.Column("usuario_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_historial_estados_pedido_usuario",
        "historial_estados_pedido",
        "usuarios",
        ["usuario_id"],
        ["id"],
    )


def downgrade() -> None:
    """Remove usuario_id column from historial_estados_pedido."""
    op.drop_constraint(
        "fk_historial_estados_pedido_usuario",
        "historial_estados_pedido",
        type_="foreignkey",
    )
    op.drop_column("historial_estados_pedido", "usuario_id")
