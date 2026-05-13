"""create_pagos_table

Revision ID: 29bdc8ae7cc6
Revises: 1702ad949a80
Create Date: 2026-05-13 08:37:57.549161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '29bdc8ae7cc6'
down_revision: Union[str, Sequence[str], None] = '1702ad949a80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create pagos table."""
    op.create_table('pagos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pedido_id', sa.Integer(), nullable=False),
        sa.Column('mp_payment_id', sa.Integer(), nullable=True),
        sa.Column('mp_status', sqlmodel.sql.sqltypes.AutoString(length=30), nullable=False, server_default='pending'),
        sa.Column('external_reference', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('idempotency_key', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('card_token', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('status_detail', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_reference'),
        sa.UniqueConstraint('idempotency_key')
    )
    op.create_index(op.f('ix_pagos_mp_payment_id'), 'pagos', ['mp_payment_id'], unique=True)
    op.create_index(op.f('ix_pagos_pedido_id'), 'pagos', ['pedido_id'], unique=False)


def downgrade() -> None:
    """Drop pagos table."""
    op.drop_index(op.f('ix_pagos_pedido_id'), table_name='pagos')
    op.drop_index(op.f('ix_pagos_mp_payment_id'), table_name='pagos')
    op.drop_table('pagos')
