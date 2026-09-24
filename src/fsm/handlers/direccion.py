"""Captura de direcciones escritas o compartidas desde WhatsApp."""

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from src.fsm.dispatcher import MensajeEntrante, ResultadoHandler
from src.fsm.handlers.pedido_finalizacion import crear_mensaje_resumen
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente
from src.services.direccion_service import (
    guardar_direccion,
    marcar_ultima_direccion,
    obtener_ultima_direccion,
)
from src.services.pedido_service import obtener_borrador

INSTRUCCION_DIRECCION = (
    "¿A qué dirección lo entregamos? Escribe calle, número y colonia, "
    "o comparte tu ubicación desde el clip 📎 > Ubicación."
)


async def mensaje_inicial_direccion(
    session: AsyncSession, cliente_id: UUID
) -> dict[str, Any]:
    """Pregunta si reutiliza la dirección más reciente o captura una nueva."""
    direccion = await obtener_ultima_direccion(session, cliente_id)
    if direccion is None:
        return {"type": "text", "body": INSTRUCCION_DIRECCION}

    detalle = direccion.texto or (
        f"Ubicación ({direccion.latitud}, {direccion.longitud})"
    )
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": f"¿Entregamos en la dirección de siempre?\n{detalle}"},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": "usar_esta", "title": "Usar esta"},
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "nueva_direccion", "title": "Nueva dirección"},
                    },
                    {"type": "reply", "reply": {"id": "volver", "title": "Volver"}},
                ]
            },
        },
    }


async def atender_captura_direccion(
    mensaje: MensajeEntrante,
    contexto: dict[str, Any],
    cliente: Cliente,
    _primera_interaccion: bool,
    *,
    session: AsyncSession,
    pedido_borrador_id: UUID | None,
) -> ResultadoHandler:
    """Guarda y asocia una dirección o reutiliza la última del cliente."""
    if mensaje.tipo == "boton" and mensaje.valor == "volver":
        return ResultadoHandler(
            EstadoConversacion.AGREGAR_MAS_O_CONTINUAR,
            contexto,
            [{"type": "text", "body": "Regresamos a tu carrito."}],
        )

    if mensaje.tipo == "boton" and mensaje.valor == "usar_esta":
        direccion = await obtener_ultima_direccion(session, cliente.id)
        if direccion is not None:
            await marcar_ultima_direccion(session, cliente.id, direccion)
            pedido = await obtener_borrador(session, cliente.id, pedido_borrador_id)
            if pedido is not None:
                pedido.direccion_id = direccion.id
                return ResultadoHandler(
                    EstadoConversacion.REVISANDO_RESUMEN,
                    contexto,
                    [await crear_mensaje_resumen(session, cliente, pedido.id)],
                )

    if mensaje.tipo == "boton" and mensaje.valor == "nueva_direccion":
        return ResultadoHandler(
            EstadoConversacion.CAPTURANDO_DIRECCION,
            contexto,
            [{"type": "text", "body": INSTRUCCION_DIRECCION}],
        )

    if mensaje.tipo == "texto":
        texto = (mensaje.valor or "").strip()
        if len(texto) < 10:
            return ResultadoHandler(
                EstadoConversacion.CAPTURANDO_DIRECCION,
                contexto,
                [
                    {
                        "type": "text",
                        "body": "La dirección es muy corta. Incluye calle, número y colonia.",
                    }
                ],
            )
        direccion = await guardar_direccion(session, cliente.id, texto=texto)
    elif mensaje.tipo == "ubicacion":
        if mensaje.latitud is None or mensaje.longitud is None:
            return ResultadoHandler(
                EstadoConversacion.CAPTURANDO_DIRECCION,
                contexto,
                [
                    {
                        "type": "text",
                        "body": "No pude leer las coordenadas. Comparte la ubicación nuevamente.",
                    }
                ],
            )
        if not -90 <= mensaje.latitud <= 90 or not -180 <= mensaje.longitud <= 180:
            return ResultadoHandler(
                EstadoConversacion.CAPTURANDO_DIRECCION,
                contexto,
                [
                    {
                        "type": "text",
                        "body": "Las coordenadas no son válidas. Comparte la ubicación nuevamente.",
                    }
                ],
            )
        ubicacion = mensaje.payload.get("location", {})
        direccion_texto = ubicacion.get("address") or ubicacion.get("name")
        direccion = await guardar_direccion(
            session,
            cliente.id,
            texto=direccion_texto if isinstance(direccion_texto, str) else None,
            latitud=Decimal(str(mensaje.latitud)),
            longitud=Decimal(str(mensaje.longitud)),
        )
    else:
        return ResultadoHandler(
            EstadoConversacion.CAPTURANDO_DIRECCION,
            contexto,
            [await mensaje_inicial_direccion(session, cliente.id)],
        )

    pedido = await obtener_borrador(session, cliente.id, pedido_borrador_id)
    if pedido is None:
        return ResultadoHandler(
            EstadoConversacion.CAPTURANDO_DIRECCION,
            contexto,
            [
                {
                    "type": "text",
                    "body": "No encontré el pedido borrador. Regresa al carrito e inténtalo de nuevo.",
                }
            ],
        )
    pedido.direccion_id = direccion.id
    return ResultadoHandler(
        EstadoConversacion.REVISANDO_RESUMEN,
        contexto,
        [await crear_mensaje_resumen(session, cliente, pedido.id)],
    )
