from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Numeric, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.cliente import Cliente
    from src.models.pedido import Pedido


class Direccion(SQLModel, table=True):
    """Dirección de entrega, escrita por el cliente o enviada como ubicación."""

    __tablename__ = "direcciones"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    cliente_id: UUID = Field(foreign_key="clientes.id", index=True)
    texto: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    latitud: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(9, 6), nullable=True),
    )
    longitud: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(9, 6), nullable=True),
    )
    es_ultima_usada: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    cliente: "Cliente" = Relationship(back_populates="direcciones")
    pedidos: list["Pedido"] = Relationship(back_populates="direccion")
