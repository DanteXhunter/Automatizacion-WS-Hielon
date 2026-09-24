"""Persistencia idempotente de eventos de mensajes de WhatsApp."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.mensaje import DireccionMensaje, Mensaje


async def registrar_mensaje_entrante(
    session: AsyncSession,
    *,
    cliente_id: UUID,
    whatsapp_message_id: str,
    tipo: str,
    contenido: dict[str, Any],
) -> bool:
    """Guarda un mensaje entrante y devuelve ``False`` si Meta lo reintentó."""
    sentencia = (
        insert(Mensaje)
        .values(
            cliente_id=cliente_id,
            direccion=DireccionMensaje.ENTRANTE,
            whatsapp_message_id=whatsapp_message_id,
            tipo=tipo,
            contenido=contenido,
            created_at=datetime.now(timezone.utc),
        )
        .on_conflict_do_nothing(index_elements=[Mensaje.whatsapp_message_id])
        .returning(Mensaje.id)
    )
    resultado = await session.exec(sentencia)
    mensaje_id = resultado.scalar_one_or_none()
    await session.commit()

    return mensaje_id is not None


async def registrar_mensaje_saliente(
    session: AsyncSession,
    *,
    cliente_id: UUID,
    whatsapp_message_id: str,
    tipo: str,
    contenido: dict[str, Any],
    pricing_category: str,
    costo_estimado: Decimal,
    pedido_id: UUID | None = None,
) -> Mensaje:
    """Guarda el resultado aceptado por Meta con su categoría y costo snapshot."""
    mensaje = Mensaje(
        cliente_id=cliente_id,
        direccion=DireccionMensaje.SALIENTE,
        whatsapp_message_id=whatsapp_message_id,
        tipo=tipo,
        contenido=contenido,
        estado="sent",
        pricing_category=pricing_category,
        costo_estimado=costo_estimado,
        pedido_id=pedido_id,
        created_at=datetime.now(timezone.utc),
    )
    session.add(mensaje)
    await session.commit()
    return mensaje
