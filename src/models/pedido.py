from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Index, Numeric, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.cliente import Cliente
    from src.models.conversacion import Conversacion
    from src.models.direccion import Direccion
    from src.models.mensaje import Mensaje
    from src.models.pedido_item import PedidoItem


class EstadoPedido(str, Enum):
    """Estados válidos del ciclo de vida de un pedido."""

    BORRADOR = "borrador"
    PENDIENTE = "pendiente"
    PROGRAMADO = "programado"
    EN_RUTA = "en_ruta"
    ENTREGADO = "entregado"
    CANCELADO_CLIENTE = "cancelado_cliente"
    CANCELADO_NEGOCIO = "cancelado_negocio"


class Pedido(SQLModel, table=True):
    """Pedido en construcción o confirmado, con su importe total congelado."""

    __tablename__ = "pedidos"
    __table_args__ = (Index("ix_pedidos_cliente_estado", "cliente_id", "estado"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    numero_orden: str | None = Field(
        default=None,
        sa_column=Column(String(30), unique=True, index=True, nullable=True),
    )
    cliente_id: UUID = Field(foreign_key="clientes.id", index=True)
    direccion_id: UUID | None = Field(
        default=None, foreign_key="direcciones.id", index=True
    )
    estado: EstadoPedido = Field(
        default=EstadoPedido.BORRADOR,
        sa_column=Column(
            SqlEnum(
                EstadoPedido,
                name="estado_pedido",
                native_enum=True,
                values_callable=lambda enum_cls: [
                    miembro.value for miembro in enum_cls
                ],
            ),
            nullable=False,
        ),
    )
    fecha_entrega: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    observaciones: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    total: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(12, 2), nullable=False),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
    )

    cliente: "Cliente" = Relationship(back_populates="pedidos")
    direccion: Optional["Direccion"] = Relationship(back_populates="pedidos")
    items: list["PedidoItem"] = Relationship(back_populates="pedido")
    conversacion_borrador: Optional["Conversacion"] = Relationship(
        back_populates="pedido_borrador",
    )
    mensajes: list["Mensaje"] = Relationship(back_populates="pedido")
