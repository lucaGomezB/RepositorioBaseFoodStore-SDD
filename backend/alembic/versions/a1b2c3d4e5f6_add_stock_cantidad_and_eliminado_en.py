"""add stock_cantidad and eliminado_en to productos

Revision ID: a1b2c3d4e5f6
Revises: 831428ec139a
Create Date: 2026-05-12 17:33:54.229000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '831428ec139a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add stock_cantidad column with default 0
    op.add_column(
        'productos',
        sa.Column('stock_cantidad', sa.Integer(), nullable=False, server_default='0'),
    )
    # Add eliminado_en column as nullable DateTime
    op.add_column(
        'productos',
        sa.Column('eliminado_en', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('productos', 'eliminado_en')
    op.drop_column('productos', 'stock_cantidad')
