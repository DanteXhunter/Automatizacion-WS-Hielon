import json
import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from src.config import settings
from src.services.cliente_service import get_or_create_por_telefono
from src.services.mensaje_service import registrar_mensaje_entrante
from src.whatsapp.client import WhatsAppAPIError, WhatsAppClient
from src.whatsapp.signature import validar_firma

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/webhook/whatsapp", response_class=PlainTextResponse)
async def verificar_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> str:
    """Responde al handshake de verificación que Meta hace al registrar la URL.

    Meta llama este endpoint una sola vez, cuando se da de alta el webhook en el
    panel. Devolver el challenge tal cual prueba que quien controla esta URL
    conoce el token acordado.

    Args:
        hub_mode: Siempre "subscribe" cuando la llamada viene de Meta.
        hub_verify_token: Token que se configuró en el panel; debe coincidir
            con el de settings.
        hub_challenge: Cadena al azar que Meta espera de vuelta sin modificar.

    Returns:
        El challenge en texto plano.

    Raises:
        HTTPException: 403 si el modo o el token no son los esperados.
    """
    if hub_mode != "subscribe" or hub_verify_token != settings.whatsapp_verify_token:
        raise HTTPException(status_code=403, detail="Verificación fallida")

    return hub_challenge


@router.post("/webhook/whatsapp")
async def recibir_evento(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Recibe los eventos de Meta, los registra y acusa recibo de inmediato.

    Este endpoint responde 200 pase lo que pase. Meta reintenta con backoff
    cualquier respuesta que no sea 200 y, si el patrón persiste, desactiva el
    webhook; recuperarlo es manual desde el panel. Por eso no se declara un
    modelo Pydantic para el body: un payload con forma inesperada produciría un
    422 automático, que Meta leería como fallo.

    Registra cada mensaje nuevo antes de programar el echo provisional. Los
    handlers de pedidos se conectarán al dispatcher en los próximos issues.

    Args:
        request: Petición cruda; el body se lee en bytes sin parsear primero.

    Returns:
        Acuse de recibo. Lo único que Meta mira es el status 200.

    Raises:
        HTTPException: 403 si la firma HMAC del header X-Hub-Signature-256
            no es válida o no viene. No revela cuál era la firma esperada.
    """
    cuerpo = await request.body()

    firma = request.headers.get("X-Hub-Signature-256")
    secreto = settings.whatsapp_app_secret.get_secret_value()
    if not validar_firma(cuerpo, firma, secreto):
        raise HTTPException(status_code=403, detail="Firma inválida")

    logger.info("Webhook recibido (%d bytes)", len(cuerpo))

    try:
        payload = json.loads(cuerpo)
        destinatarios = await _registrar_eventos(payload)
        cliente_whatsapp: WhatsAppClient = request.app.state.whatsapp_client
        for destinatario in destinatarios:
            background_tasks.add_task(
                _responder_echo,
                cliente_whatsapp,
                destinatario,
            )
    except json.JSONDecodeError:
        logger.warning("El body del webhook no es JSON válido; se ignora")
    except Exception:
        logger.exception("Error inesperado al interpretar el webhook; se ignora")

    return {"status": "received"}


async def _registrar_eventos(payload: Any) -> list[str]:
    """Registra eventos y devuelve teléfonos con mensaje nuevo para el echo.

    Meta anida los eventos en entry[] -> changes[] -> value, y ambas son listas
    que pueden traer varios elementos en un mismo request. Dentro de value
    llegan dos cosas distintas por el mismo endpoint: mensajes de clientes
    ("messages") y cambios de estado de mensajes que enviamos ("statuses").

    Args:
        payload: Body del webhook ya parseado. Puede tener cualquier forma; el
            llamador atrapa lo que falle.
    """
    destinatarios: list[str] = []

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            for mensaje in value.get("messages", []):
                destinatario = await _registrar_mensaje_entrante(value, mensaje)
                if destinatario is not None:
                    destinatarios.append(destinatario)

            for status in value.get("statuses", []):
                logger.info(
                    "Status de mensaje | id=%s estado=%s destinatario=%s",
                    status.get("id"),
                    status.get("status"),
                    status.get("recipient_id"),
                )

    return destinatarios


async def _responder_echo(
    cliente_whatsapp: WhatsAppClient,
    destinatario: str,
) -> None:
    """Envía el echo sin convertir un fallo de Meta en un fallo del webhook."""
    try:
        await cliente_whatsapp.enviar_texto(destinatario, "Recibí tu mensaje")
    except WhatsAppAPIError:
        logger.exception("No se pudo enviar el echo al destinatario")


async def _registrar_mensaje_entrante(
    value: dict[str, Any],
    mensaje: dict[str, Any],
) -> str | None:
    """Persiste un mensaje nuevo antes de permitir efectos conversacionales."""
    whatsapp_message_id = mensaje.get("id")
    telefono = mensaje.get("from")
    if not isinstance(whatsapp_message_id, str) or not isinstance(telefono, str):
        logger.warning("Mensaje entrante sin id o teléfono; se ignora")
        return None

    from src.database import session_factory

    async with session_factory() as session:
        cliente = await get_or_create_por_telefono(
            session,
            telefono,
            _obtener_nombre_del_perfil(value, telefono),
        )
        es_nuevo = await registrar_mensaje_entrante(
            session,
            cliente_id=cliente.id,
            whatsapp_message_id=whatsapp_message_id,
            tipo=str(mensaje.get("type", "desconocido")),
            contenido=mensaje,
        )

    if not es_nuevo:
        logger.info("Mensaje duplicado ignorado | id=%s", whatsapp_message_id)
        return None

    logger.info(
        "Mensaje entrante registrado | id=%s de=%s tipo=%s",
        whatsapp_message_id,
        telefono,
        mensaje.get("type"),
    )
    return telefono


def _obtener_nombre_del_perfil(value: dict[str, Any], telefono: str) -> str | None:
    """Extrae el nombre de perfil del contacto que mandó el mensaje."""
    for contacto in value.get("contacts", []):
        if contacto.get("wa_id") != telefono:
            continue

        perfil = contacto.get("profile", {})
        nombre = perfil.get("name")
        return nombre if isinstance(nombre, str) else None

    return None
