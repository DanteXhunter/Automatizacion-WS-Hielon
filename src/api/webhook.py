import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from src.config import settings
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
async def recibir_evento(request: Request) -> dict[str, str]:
    """Recibe los eventos de Meta, los registra y acusa recibo de inmediato.

    Este endpoint responde 200 pase lo que pase. Meta reintenta con backoff
    cualquier respuesta que no sea 200 y, si el patrón persiste, desactiva el
    webhook; recuperarlo es manual desde el panel. Por eso no se declara un
    modelo Pydantic para el body: un payload con forma inesperada produciría un
    422 automático, que Meta leería como fallo.

    De momento solo registra lo que llega. El procesamiento real es Fase 2.

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

    logger.info("Webhook recibido (%d bytes): %s", len(cuerpo), cuerpo.decode("utf-8", "replace"))

    try:
        payload = json.loads(cuerpo)
        _registrar_eventos(payload)
    except json.JSONDecodeError:
        logger.warning("El body del webhook no es JSON válido; se ignora")
    except Exception:
        logger.exception("Error inesperado al interpretar el webhook; se ignora")

    return {"status": "received"}


def _registrar_eventos(payload: Any) -> None:
    """Recorre el payload de Meta y loguea por separado mensajes y statuses.

    Meta anida los eventos en entry[] -> changes[] -> value, y ambas son listas
    que pueden traer varios elementos en un mismo request. Dentro de value
    llegan dos cosas distintas por el mismo endpoint: mensajes de clientes
    ("messages") y cambios de estado de mensajes que enviamos ("statuses").

    Args:
        payload: Body del webhook ya parseado. Puede tener cualquier forma; el
            llamador atrapa lo que falle.
    """
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            for mensaje in value.get("messages", []):
                logger.info(
                    "Mensaje entrante | id=%s de=%s tipo=%s",
                    mensaje.get("id"),
                    mensaje.get("from"),
                    mensaje.get("type"),
                )

            for status in value.get("statuses", []):
                logger.info(
                    "Status de mensaje | id=%s estado=%s destinatario=%s",
                    status.get("id"),
                    status.get("status"),
                    status.get("recipient_id"),
                )
