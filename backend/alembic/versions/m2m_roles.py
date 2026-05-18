"""Add usuarios_roles pivot table for M2M roles

Revision ID: m2m_roles
Revises: 1702ad949a80
"""
from typing import Union
from alembic import op
import sqlalchemy as sa


revision: str = 'm2m_roles'
down_revision: Union[str, None] = '3b0a6a81a001'


def upgrade() -> None:
    # Create usuarios_roles pivot table
    op.create_table('usuarios_roles',
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('rol_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    )

    # Migrate existing rol_id data from usuarios to usuarios_roles
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id, rol_id FROM usuarios WHERE rol_id IS NOT NULL"))
    rows = result.fetchall()
    for row in rows:
        conn.execute(
            sa.text("INSERT INTO usuarios_roles (usuario_id, rol_id) VALUES (:uid, :rid)"),
            {"uid": row[0], "rid": row[1]},
        )


def downgrade() -> None:
    op.drop_table('usuarios_roles')
