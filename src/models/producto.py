from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, Numeric, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.pedido_item import PedidoItem


class Producto(SQLModel, table=True):
    """Producto activo del catálogo que puede incluirse en un pedido."""

    __tablename__ = "productos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre: str = Field(sa_column=Column(String(100), nullable=False))
    peso_kg: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False))
    dimensiones: str | None = Field(
        default=None, sa_column=Column(String(100), nullable=True)
    )
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    activo: bool = Field(default=True, nullable=False)

    pedido_items: list["PedidoItem"] = Relationship(back_populates="producto")
