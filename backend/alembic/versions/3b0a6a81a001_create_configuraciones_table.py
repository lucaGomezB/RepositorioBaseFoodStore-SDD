"""create_configuraciones_table

Revision ID: 3b0a6a81a001
Revises: 29bdc8ae7cc6
Create Date: 2026-05-13 09:18:44.480596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '3b0a6a81a001'
down_revision: Union[str, Sequence[str], None] = '29bdc8ae7cc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create configuraciones table."""
    op.create_table('configuraciones',
        sa.Column('clave', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('valor', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column('descripcion', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('clave'),
    )


def downgrade() -> None:
    """Drop configuraciones table."""
    op.drop_table('configuraciones')
