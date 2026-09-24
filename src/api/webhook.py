import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import settings
from src.fsm.dispatcher import DispatcherConversacion, normalizar_mensaje
from src.fsm.handlers.direccion import atender_captura_direccion
from src.fsm.handlers.idle import atender_idle
from src.fsm.handlers.menu_principal import atender_asesor, atender_menu_principal
from src.fsm.handlers.pedido import (
    atender_captura_cantidad,
    atender_carrito,
    atender_seleccion_producto,
)
from src.fsm.handlers.pedido_finalizacion import (
    atender_confirmacion_cancelacion,
    atender_revision_resumen,
    atender_seleccion_modificacion,
)
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente
from src.models.conversacion import Conversacion
from src.services.cliente_service import get_or_create_por_telefono
from src.services.locks import bloqueo_por_cliente
from src.services.mensaje_service import registrar_mensaje_entrante
from src.utils.datetime import ahora_local, es_horario_laboral
from src.whatsapp.client import WhatsAppAPIError, WhatsAppClient
from src.whatsapp.signature import validar_firma

logger = logging.getLogger(__name__)

AVISO_FUERA_DE_HORARIO = (
    "Gracias por escribirnos. Nuestro horario es de lunes a sábado de "
    "7:00 a 17:00. Te atendemos en cuanto abramos."
)
INTERVALO_AVISO_FUERA_DE_HORARIO = timedelta(hours=1)

router = APIRouter()
dispatcher = DispatcherConversacion(
    {
        EstadoConversacion.IDLE: atender_idle,
        EstadoConversacion.MENU_PRINCIPAL: atender_menu_principal,
        EstadoConversacion.EN_ASESOR_HUMANO: atender_asesor,
        EstadoConversacion.SELECCIONANDO_PRODUCTO: atender_seleccion_producto,
        EstadoConversacion.CAPTURANDO_CANTIDAD: atender_captura_cantidad,
        EstadoConversacion.AGREGAR_MAS_O_CONTINUAR: atender_carrito,
        EstadoConversacion.CAPTURANDO_DIRECCION: atender_captura_direccion,
        EstadoConversacion.REVISANDO_RESUMEN: atender_revision_resumen,
        EstadoConversacion.SELECCIONANDO_MODIFICACION: atender_seleccion_modificacion,
        EstadoConversacion.CONFIRMANDO_CANCELACION: atender_confirmacion_cancelacion,
    }
)


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

    Registra cada mensaje nuevo antes de programar su paso por la FSM.

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
        eventos = await _registrar_eventos(payload)
        cliente_whatsapp: WhatsAppClient = request.app.state.whatsapp_client
        for cliente, mensaje in eventos:
            background_tasks.add_task(
                _procesar_mensaje,
                cliente_whatsapp,
                cliente,
                mensaje,
            )
    except json.JSONDecodeError:
        logger.warning("El body del webhook no es JSON válido; se ignora")
    except Exception:
        logger.exception("Error inesperado al interpretar el webhook; se ignora")

    return {"status": "received"}


async def _registrar_eventos(payload: Any) -> list[tuple[Cliente, dict[str, Any]]]:
    """Registra eventos y devuelve los mensajes nuevos para la FSM.

    Meta anida los eventos en entry[] -> changes[] -> value, y ambas son listas
    que pueden traer varios elementos en un mismo request. Dentro de value
    llegan dos cosas distintas por el mismo endpoint: mensajes de clientes
    ("messages") y cambios de estado de mensajes que enviamos ("statuses").

    Args:
        payload: Body del webhook ya parseado. Puede tener cualquier forma; el
            llamador atrapa lo que falle.
    """
    eventos: list[tuple[Cliente, dict[str, Any]]] = []

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            for mensaje in value.get("messages", []):
                cliente = await _registrar_mensaje_entrante(value, mensaje)
                if cliente is not None:
                    eventos.append((cliente, mensaje))

            for status in value.get("statuses", []):
                logger.info(
                    "Status de mensaje | id=%s estado=%s destinatario=%s",
                    status.get("id"),
                    status.get("status"),
                    status.get("recipient_id"),
                )

    return eventos


async def _procesar_mensaje(
    cliente_whatsapp: WhatsAppClient,
    cliente: Cliente,
    mensaje: dict[str, Any],
) -> None:
    """Aplica la FSM y envía sus respuestas después de guardar el nuevo estado."""
    from src.database import session_factory

    async def enviar_mensajes(
        destinatario: Cliente, mensajes: list[dict[str, Any]]
    ) -> None:
        telefono = destinatario.telefono.removeprefix("+")
        for saliente in mensajes:
            if saliente["type"] == "interactive":
                await cliente_whatsapp.enviar_interactivo(
                    telefono, saliente["interactive"]
                )
            elif saliente["type"] == "text":
                await cliente_whatsapp.enviar_texto(telefono, saliente["body"])

    try:
        async with session_factory() as session:
            if not es_horario_laboral():
                enviar_aviso = await _registrar_aviso_fuera_de_horario(
                    session,
                    cliente,
                )
                if enviar_aviso:
                    telefono = cliente.telefono.removeprefix("+")
                    await cliente_whatsapp.enviar_texto(
                        telefono,
                        AVISO_FUERA_DE_HORARIO,
                    )
                return
            await dispatcher.procesar(
                session,
                cliente,
                normalizar_mensaje(mensaje),
                enviar_mensajes=enviar_mensajes,
            )
    except WhatsAppAPIError:
        logger.exception("No se pudo enviar una respuesta al cliente_id=%s", cliente.id)
    except Exception:
        logger.exception(
            "No se pudo procesar la conversación del cliente_id=%s", cliente.id
        )


async def _registrar_aviso_fuera_de_horario(
    session: AsyncSession,
    cliente: Cliente,
    *,
    instante: datetime | None = None,
) -> bool:
    """Conserva la FSM y limita el aviso fuera de horario a uno por hora."""
    momento = instante or ahora_local()
    async with bloqueo_por_cliente(session, cliente.id):
        conversacion = (
            await session.exec(
                select(Conversacion).where(Conversacion.cliente_id == cliente.id)
            )
        ).first()
        if conversacion is None:
            conversacion = Conversacion(cliente_id=cliente.id)
            session.add(conversacion)

        contexto = conversacion.contexto.copy()
        ultimo_texto = contexto.get("ultimo_aviso_fuera_horario")
        if isinstance(ultimo_texto, str):
            try:
                ultimo = datetime.fromisoformat(ultimo_texto)
            except ValueError:
                ultimo = None
            if ultimo is not None and ultimo.tzinfo is None:
                ultimo = ultimo.replace(tzinfo=momento.tzinfo)
            if (
                ultimo is not None
                and momento - ultimo < INTERVALO_AVISO_FUERA_DE_HORARIO
            ):
                conversacion.ultima_interaccion = momento.astimezone(timezone.utc)
                await session.commit()
                return False

        contexto["ultimo_aviso_fuera_horario"] = momento.isoformat()
        conversacion.contexto = contexto
        conversacion.ultima_interaccion = momento.astimezone(timezone.utc)
        await session.commit()
        return True


async def _registrar_mensaje_entrante(
    value: dict[str, Any],
    mensaje: dict[str, Any],
) -> Cliente | None:
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
    return cliente


def _obtener_nombre_del_perfil(value: dict[str, Any], telefono: str) -> str | None:
    """Extrae el nombre de perfil del contacto que mandó el mensaje."""
    for contacto in value.get("contacts", []):
        if contacto.get("wa_id") != telefono:
            continue

        perfil = contacto.get("profile", {})
        nombre = perfil.get("name")
        return nombre if isinstance(nombre, str) else None

    return None
