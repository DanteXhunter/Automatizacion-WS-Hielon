from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.pedido import Pedido
    from src.models.producto import Producto


class PedidoItem(SQLModel, table=True):
    """Renglón de un pedido con el precio vigente al momento de capturarlo."""

    __tablename__ = "pedido_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pedido_id: UUID = Field(foreign_key="pedidos.id", index=True)
    producto_id: UUID = Field(foreign_key="productos.id", index=True)
    cantidad: int = Field(gt=0, nullable=False)
    precio_unitario: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    subtotal: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))

    pedido: "Pedido" = Relationship(back_populates="items")
    producto: "Producto" = Relationship(back_populates="pedido_items")
