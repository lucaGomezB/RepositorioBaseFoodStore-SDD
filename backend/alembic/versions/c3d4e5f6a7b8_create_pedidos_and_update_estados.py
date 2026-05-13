"""create pedidos, detalles_pedido, historial_estados and migrate estado_pedido

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-12 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ------------------------------------------------------------------
    # 1. Create estados_pedido table (replaces estado_pedido)
    # ------------------------------------------------------------------
    op.create_table(
        "estados_pedido",
        sa.Column("codigo", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("nombre", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("descripcion", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("es_terminal", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("codigo"),
    )

    # Migrate data from old estado_pedido to new estados_pedido
    # Map old integer IDs to semantic codes + set orden/es_terminal
    conn = op.get_bind()
    old_table = sa.table(
        "estado_pedido",
        sa.column("id", sa.Integer),
        sa.column("nombre", sa.String),
        sa.column("descripcion", sa.String),
    )
    result = conn.execute(sa.select(old_table)).fetchall()

    estado_map = {
        1: {"codigo": "PENDIENTE", "orden": 1, "es_terminal": False},
        2: {"codigo": "CONFIRMADO", "orden": 2, "es_terminal": False},
        3: {"codigo": "EN_PREPARACION", "orden": 3, "es_terminal": False},
        4: {"codigo": "EN_CAMINO", "orden": 4, "es_terminal": False},
        5: {"codigo": "ENTREGADO", "orden": 5, "es_terminal": True},
        6: {"codigo": "CANCELADO", "orden": 6, "es_terminal": True},
    }

    for row in result:
        mapping = estado_map.get(row.id, {})
        if mapping:
            new_table = sa.table(
                "estados_pedido",
                sa.column("codigo", sa.String),
                sa.column("nombre", sa.String),
                sa.column("descripcion", sa.String),
                sa.column("orden", sa.Integer),
                sa.column("es_terminal", sa.Boolean),
            )
            conn.execute(
                new_table.insert().values(
                    codigo=mapping["codigo"],
                    nombre=row.nombre.title() if row.nombre.isupper() else row.nombre,
                    descripcion=row.descripcion,
                    orden=mapping["orden"],
                    es_terminal=mapping["es_terminal"],
                )
            )

    # Drop old estado_pedido table
    op.drop_table("estado_pedido")

    # ------------------------------------------------------------------
    # 2. Create pedidos table
    # ------------------------------------------------------------------
    op.create_table(
        "pedidos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("estado_codigo", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False, server_default="PENDIENTE"),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column("costo_envio", sa.Float(), nullable=False),
        sa.Column("forma_pago_codigo", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column("direccion_calle", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("direccion_numero", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("direccion_piso", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("direccion_ciudad", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("direccion_cp", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ),
        sa.ForeignKeyConstraint(["estado_codigo"], ["estados_pedido.codigo"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------
    # 3. Create detalles_pedido table
    # ------------------------------------------------------------------
    op.create_table(
        "detalles_pedido",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("producto_id", sa.Integer(), nullable=False),
        sa.Column("nombre_snapshot", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("precio_snapshot", sa.Float(), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("exclusiones", sa.JSON(), nullable=True),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"], ),
        sa.ForeignKeyConstraint(["producto_id"], ["productos.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------
    # 4. Create historial_estados_pedido table
    # ------------------------------------------------------------------
    op.create_table(
        "historial_estados_pedido",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("estado_desde", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column("estado_hacia", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("motivo", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop historial_estados_pedido
    op.drop_table("historial_estados_pedido")
    # Drop detalles_pedido
    op.drop_table("detalles_pedido")
    # Drop pedidos
    op.drop_table("pedidos")
    # Drop estados_pedido and recreate old estado_pedido
    op.drop_table("estados_pedido")

    op.create_table(
        "estado_pedido",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("descripcion", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
    )
