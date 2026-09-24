from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.cliente import Cliente
    from src.models.pedido import Pedido


class Conversacion(SQLModel, table=True):
    """Estado persistente de la FSM para un único cliente."""

    __tablename__ = "conversaciones"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    cliente_id: UUID = Field(foreign_key="clientes.id", unique=True, index=True)
    estado_actual: str = Field(
        default="IDLE",
        sa_column=Column(String(80), nullable=False),
    )
    estado_anterior: str | None = Field(
        default=None, sa_column=Column(String(80), nullable=True)
    )
    contexto: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False),
    )
    pedido_borrador_id: UUID | None = Field(default=None, foreign_key="pedidos.id")
    ultima_interaccion: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    version: int = Field(default=1, nullable=False)

    cliente: "Cliente" = Relationship(back_populates="conversacion")
    pedido_borrador: Optional["Pedido"] = Relationship(
        back_populates="conversacion_borrador"
    )
