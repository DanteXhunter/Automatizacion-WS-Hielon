"""Persistencia idempotente de eventos de mensajes de WhatsApp."""

from datetime import datetime, timezone
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
