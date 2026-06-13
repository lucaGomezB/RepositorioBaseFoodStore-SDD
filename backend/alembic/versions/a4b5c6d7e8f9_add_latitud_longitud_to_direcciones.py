"""add latitud/longitud columns to direcciones

Revision ID: a4b5c6d7e8f9
Revises: 8697707896ca
Create Date: 2026-06-13 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4b5c6d7e8f9'
down_revision: Union[str, Sequence[str], None] = '8697707896ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add latitud and longitud columns to direcciones table."""
    op.add_column('direcciones', sa.Column('latitud', sa.Float(), nullable=True))
    op.add_column('direcciones', sa.Column('longitud', sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove latitud and longitud columns from direcciones table."""
    op.drop_column('direcciones', 'latitud')
    op.drop_column('direcciones', 'longitud')
