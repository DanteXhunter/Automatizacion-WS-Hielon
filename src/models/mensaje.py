from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Numeric, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.cliente import Cliente
    from src.models.pedido import Pedido


class DireccionMensaje(str, Enum):
    """Sentido de un mensaje respecto al negocio."""

    ENTRANTE = "entrante"
    SALIENTE = "saliente"


class Mensaje(SQLModel, table=True):
    """Evento entrante o saliente que sirve para trazabilidad e idempotencia."""

    __tablename__ = "mensajes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    cliente_id: UUID = Field(foreign_key="clientes.id", index=True)
    direccion: DireccionMensaje = Field(
        sa_column=Column(
            SqlEnum(
                DireccionMensaje,
                name="direccion_mensaje",
                native_enum=True,
                values_callable=lambda enum_cls: [
                    miembro.value for miembro in enum_cls
                ],
            ),
            nullable=False,
        ),
    )
    whatsapp_message_id: str = Field(
        sa_column=Column(String(150), unique=True, index=True, nullable=False),
    )
    tipo: str = Field(sa_column=Column(String(50), nullable=False))
    contenido: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    estado: str | None = Field(
        default=None, sa_column=Column(String(50), nullable=True)
    )
    pricing_category: str | None = Field(
        default=None,
        sa_column=Column(String(50), nullable=True),
    )
    costo_estimado: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(10, 4), nullable=True),
    )
    pedido_id: UUID | None = Field(default=None, foreign_key="pedidos.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    cliente: "Cliente" = Relationship(back_populates="mensajes")
    pedido: Optional["Pedido"] = Relationship(back_populates="mensajes")
