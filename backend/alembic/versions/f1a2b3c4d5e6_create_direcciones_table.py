"""create_direcciones_table

Revision ID: f1a2b3c4d5e6
Revises: e1f2a3b4c5d6
Create Date: 2026-05-12 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'e1f2a3b4c5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'direcciones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('calle', sa.String(length=255), nullable=False),
        sa.Column('numero', sa.String(length=20), nullable=False),
        sa.Column('piso_depto', sa.String(length=50), nullable=True),
        sa.Column('ciudad', sa.String(length=100), nullable=False),
        sa.Column('codigo_postal', sa.String(length=20), nullable=False),
        sa.Column('es_predeterminada', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_direcciones_usuario_id'), 'direcciones', ['usuario_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_direcciones_usuario_id'), table_name='direcciones')
    op.drop_table('direcciones')
