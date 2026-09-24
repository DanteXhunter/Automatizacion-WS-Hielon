"""Notificación operativa del handoff al responsable por WhatsApp."""

import logging
import re

from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import settings
from src.models.cliente import Cliente
from src.services.mensaje_service import registrar_mensaje_saliente
from src.whatsapp.client import WhatsAppAPIError, WhatsAppClient

logger = logging.getLogger(__name__)

NOMBRE_PLANTILLA_HANDOFF = "handoff_asesor"
IDIOMA_PLANTILLA_HANDOFF = "es_MX"
LIMITE_PARAMETRO = 200


def sanitizar_parametro(valor: str, limite: int = LIMITE_PARAMETRO) -> str:
    """Convierte espacios problemáticos en uno solo y limita el texto."""
    limpio = re.sub(r"\s+", " ", valor).strip()
    return limpio[:limite] or "Sin información"


async def notificar_handoff(
    session: AsyncSession,
    cliente_whatsapp: WhatsAppClient,
    cliente: Cliente,
    *,
    motivo: str,
    ultimo_mensaje: str,
) -> bool:
    """Avisa al administrador sin permitir que una falla revierta el handoff."""
    telefono_admin = settings.whatsapp_telefono_admin
    if not telefono_admin:
        logger.error(
            "No se notificó el handoff del cliente_id=%s: falta WHATSAPP_TELEFONO_ADMIN",
            cliente.id,
        )
        return False

    parametros = [
        sanitizar_parametro(cliente.nombre or "Sin registrar"),
        sanitizar_parametro(cliente.telefono),
        sanitizar_parametro(motivo),
        sanitizar_parametro(ultimo_mensaje),
    ]
    contenido = {
        "template": {
            "name": NOMBRE_PLANTILLA_HANDOFF,
            "language": IDIOMA_PLANTILLA_HANDOFF,
            "parameters": parametros,
        }
    }

    try:
        message_id = await cliente_whatsapp.enviar_plantilla(
            telefono_admin.removeprefix("+"),
            NOMBRE_PLANTILLA_HANDOFF,
            IDIOMA_PLANTILLA_HANDOFF,
            parametros,
        )
        await registrar_mensaje_saliente(
            session,
            cliente_id=cliente.id,
            whatsapp_message_id=message_id,
            tipo="template",
            contenido=contenido,
            pricing_category="utility",
            costo_estimado=settings.tarifa_utility_mxn,
            pedido_id=None,
        )
    except WhatsAppAPIError:
        logger.exception(
            "Falló la notificación de handoff para cliente_id=%s",
            cliente.id,
        )
        return False
    except Exception:
        logger.exception(
            "La notificación de handoff se envió o registró de forma incompleta "
            "para cliente_id=%s",
            cliente.id,
        )
        return False

    return True
