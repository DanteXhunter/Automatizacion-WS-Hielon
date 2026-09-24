"""contador anual atomico para folios de pedido

Revision ID: 4f9a2c7d1b30
Revises: c81aeeee9d64
Create Date: 2026-09-24

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "4f9a2c7d1b30"
down_revision: str | Sequence[str] | None = "c81aeeee9d64"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crea un contador independiente para cada año calendario."""
    op.create_table(
        "folios_pedido_anuales",
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("ultimo_valor", sa.Integer(), nullable=False),
        sa.CheckConstraint("ultimo_valor > 0", name="ck_folio_ultimo_valor_positivo"),
        sa.PrimaryKeyConstraint("anio"),
    )


def downgrade() -> None:
    """Elimina el contador; los folios ya asignados permanecen en pedidos."""
    op.drop_table("folios_pedido_anuales")
