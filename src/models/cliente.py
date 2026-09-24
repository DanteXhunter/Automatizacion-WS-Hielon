from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.conversacion import Conversacion
    from src.models.direccion import Direccion
    from src.models.mensaje import Mensaje
    from src.models.pedido import Pedido


class Cliente(SQLModel, table=True):
    """Persona o negocio que escribe al número de WhatsApp de Hielon."""

    __tablename__ = "clientes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    telefono: str = Field(
        sa_column=Column(String(20), unique=True, index=True, nullable=False),
    )
    nombre: str | None = Field(
        default=None, sa_column=Column(String(120), nullable=True)
    )
    opt_in_recordatorios: bool = Field(default=False, nullable=False)
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

    direcciones: list["Direccion"] = Relationship(back_populates="cliente")
    pedidos: list["Pedido"] = Relationship(back_populates="cliente")
    conversacion: Optional["Conversacion"] = Relationship(back_populates="cliente")
    mensajes: list["Mensaje"] = Relationship(back_populates="cliente")
