"""add latitud/longitud columns to pedidos

Revision ID: 8697707896ca
Revises: m2m_roles
Create Date: 2026-05-18 08:02:13.341218

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8697707896ca'
down_revision: Union[str, Sequence[str], None] = 'm2m_roles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add latitud and longitud columns to pedidos table."""
    op.add_column('pedidos', sa.Column('latitud', sa.Float(), nullable=True))
    op.add_column('pedidos', sa.Column('longitud', sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove latitud and longitud columns from pedidos table."""
    op.drop_column('pedidos', 'latitud')
    op.drop_column('pedidos', 'longitud')
