"""esquema inicial

Revision ID: c81aeeee9d64
Revises:
Create Date: 2026-09-23 19:46:01.224708

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c81aeeee9d64"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

estado_pedido = postgresql.ENUM(
    "borrador",
    "pendiente",
    "programado",
    "en_ruta",
    "entregado",
    "cancelado_cliente",
    "cancelado_negocio",
    name="estado_pedido",
    create_type=False,
)

direccion_mensaje = postgresql.ENUM(
    "entrante",
    "saliente",
    name="direccion_mensaje",
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    estado_pedido.create(op.get_bind(), checkfirst=True)
    direccion_mensaje.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "clientes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("telefono", sa.String(length=20), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=True),
        sa.Column("opt_in_recordatorios", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clientes_telefono"), "clientes", ["telefono"], unique=True)
    op.create_table(
        "productos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("peso_kg", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("dimensiones", sa.String(length=100), nullable=True),
        sa.Column("precio", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "direcciones",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cliente_id", sa.Uuid(), nullable=False),
        sa.Column("texto", sa.Text(), nullable=True),
        sa.Column("latitud", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitud", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("es_ultima_usada", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_direcciones_cliente_id"), "direcciones", ["cliente_id"], unique=False
    )
    op.create_table(
        "pedidos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("numero_orden", sa.String(length=30), nullable=True),
        sa.Column("cliente_id", sa.Uuid(), nullable=False),
        sa.Column("direccion_id", sa.Uuid(), nullable=True),
        sa.Column(
            "estado",
            estado_pedido,
            nullable=False,
        ),
        sa.Column("fecha_entrega", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["direccion_id"],
            ["direcciones.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_pedidos_cliente_estado", "pedidos", ["cliente_id", "estado"], unique=False
    )
    op.create_index(
        op.f("ix_pedidos_cliente_id"), "pedidos", ["cliente_id"], unique=False
    )
    op.create_index(
        op.f("ix_pedidos_direccion_id"), "pedidos", ["direccion_id"], unique=False
    )
    op.create_index(
        op.f("ix_pedidos_numero_orden"), "pedidos", ["numero_orden"], unique=True
    )
    op.create_table(
        "conversaciones",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cliente_id", sa.Uuid(), nullable=False),
        sa.Column("estado_actual", sa.String(length=80), nullable=False),
        sa.Column("estado_anterior", sa.String(length=80), nullable=True),
        sa.Column("contexto", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("pedido_borrador_id", sa.Uuid(), nullable=True),
        sa.Column("ultima_interaccion", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pedido_borrador_id"],
            ["pedidos.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_conversaciones_cliente_id"),
        "conversaciones",
        ["cliente_id"],
        unique=True,
    )
    op.create_table(
        "mensajes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cliente_id", sa.Uuid(), nullable=False),
        sa.Column(
            "direccion",
            direccion_mensaje,
            nullable=False,
        ),
        sa.Column("whatsapp_message_id", sa.String(length=150), nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("contenido", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("estado", sa.String(length=50), nullable=True),
        sa.Column("pricing_category", sa.String(length=50), nullable=True),
        sa.Column("costo_estimado", sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column("pedido_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pedido_id"],
            ["pedidos.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mensajes_cliente_id"), "mensajes", ["cliente_id"], unique=False
    )
    op.create_index(
        op.f("ix_mensajes_pedido_id"), "mensajes", ["pedido_id"], unique=False
    )
    op.create_index(
        op.f("ix_mensajes_whatsapp_message_id"),
        "mensajes",
        ["whatsapp_message_id"],
        unique=True,
    )
    op.create_table(
        "pedido_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("pedido_id", sa.Uuid(), nullable=False),
        sa.Column("producto_id", sa.Uuid(), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.ForeignKeyConstraint(
            ["pedido_id"],
            ["pedidos.id"],
        ),
        sa.ForeignKeyConstraint(
            ["producto_id"],
            ["productos.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pedido_items_pedido_id"), "pedido_items", ["pedido_id"], unique=False
    )
    op.create_index(
        op.f("ix_pedido_items_producto_id"),
        "pedido_items",
        ["producto_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_pedido_items_producto_id"), table_name="pedido_items")
    op.drop_index(op.f("ix_pedido_items_pedido_id"), table_name="pedido_items")
    op.drop_table("pedido_items")
    op.drop_index(op.f("ix_mensajes_whatsapp_message_id"), table_name="mensajes")
    op.drop_index(op.f("ix_mensajes_pedido_id"), table_name="mensajes")
    op.drop_index(op.f("ix_mensajes_cliente_id"), table_name="mensajes")
    op.drop_table("mensajes")
    op.drop_index(op.f("ix_conversaciones_cliente_id"), table_name="conversaciones")
    op.drop_table("conversaciones")
    op.drop_index(op.f("ix_pedidos_numero_orden"), table_name="pedidos")
    op.drop_index(op.f("ix_pedidos_direccion_id"), table_name="pedidos")
    op.drop_index(op.f("ix_pedidos_cliente_id"), table_name="pedidos")
    op.drop_index("ix_pedidos_cliente_estado", table_name="pedidos")
    op.drop_table("pedidos")
    op.drop_index(op.f("ix_direcciones_cliente_id"), table_name="direcciones")
    op.drop_table("direcciones")
    op.drop_table("productos")
    op.drop_index(op.f("ix_clientes_telefono"), table_name="clientes")
    op.drop_table("clientes")
    direccion_mensaje.drop(op.get_bind(), checkfirst=True)
    estado_pedido.drop(op.get_bind(), checkfirst=True)
