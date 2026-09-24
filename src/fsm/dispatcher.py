"""Enrutamiento transaccional de mensajes hacia handlers de conversación."""

import logging
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.fsm.states import EstadoConversacion, es_transicion_valida
from src.models.cliente import Cliente
from src.models.conversacion import Conversacion

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MensajeEntrante:
    """Representación uniforme de texto, botón, lista o ubicación de Meta."""

    tipo: str
    valor: str | None
    payload: dict[str, Any]
    latitud: float | None = None
    longitud: float | None = None


@dataclass(frozen=True)
class ResultadoHandler:
    """Decisión pura de un handler, lista para persistirse y luego enviarse."""

    siguiente_estado: EstadoConversacion
    contexto: dict[str, Any]
    mensajes_salientes: list[dict[str, Any]]


HandlerConversacion = Callable[
    [MensajeEntrante, dict[str, Any], Cliente],
    ResultadoHandler,
]
EmisorMensajes = Callable[[Cliente, list[dict[str, Any]]], Awaitable[None]]


class HandlerNoRegistradoError(LookupError):
    """Señala que el estado guardado no tiene una implementación disponible."""


def normalizar_mensaje(mensaje: dict[str, Any]) -> MensajeEntrante:
    """Aplana las variantes de payload de Meta para los handlers de la FSM."""
    tipo_meta = str(mensaje.get("type", "desconocido"))

    if tipo_meta == "text":
        texto = mensaje.get("text", {}).get("body")
        return MensajeEntrante(
            tipo="texto",
            valor=texto if isinstance(texto, str) else None,
            payload=mensaje,
        )

    if tipo_meta == "interactive":
        interactivo = mensaje.get("interactive", {})
        respuesta = interactivo.get("button_reply") or interactivo.get("list_reply")
        valor = respuesta.get("id") if isinstance(respuesta, dict) else None
        return MensajeEntrante(
            tipo="boton",
            valor=valor if isinstance(valor, str) else None,
            payload=mensaje,
        )

    if tipo_meta == "location":
        ubicacion = mensaje.get("location", {})
        latitud = ubicacion.get("latitude")
        longitud = ubicacion.get("longitude")
        return MensajeEntrante(
            tipo="ubicacion",
            valor=None,
            payload=mensaje,
            latitud=float(latitud) if isinstance(latitud, int | float) else None,
            longitud=float(longitud) if isinstance(longitud, int | float) else None,
        )

    return MensajeEntrante(tipo=tipo_meta, valor=None, payload=mensaje)


class DispatcherConversacion:
    """Carga una conversación, ejecuta su handler y persiste su transición."""

    def __init__(self, handlers: Mapping[EstadoConversacion, HandlerConversacion]):
        self._handlers = dict(handlers)

    async def procesar(
        self,
        session: AsyncSession,
        cliente: Cliente,
        mensaje: MensajeEntrante,
        *,
        enviar_mensajes: EmisorMensajes | None = None,
    ) -> ResultadoHandler | None:
        """Persiste una transición válida y envía respuestas solo tras el commit.

        TODO(#31): rodear esta operación con un advisory lock por ``cliente.id``.
        """
        conversacion = await self._obtener_o_crear_conversacion(session, cliente.id)
        estado_origen = EstadoConversacion(conversacion.estado_actual)
        handler = self._handlers.get(estado_origen)
        if handler is None:
            await session.rollback()
            raise HandlerNoRegistradoError(
                f"No hay handler registrado para el estado {estado_origen.value}."
            )

        resultado = handler(mensaje, conversacion.contexto.copy(), cliente)
        if not es_transicion_valida(estado_origen, resultado.siguiente_estado):
            logger.warning(
                "Transición inválida descartada | cliente_id=%s origen=%s destino=%s",
                cliente.id,
                estado_origen.value,
                resultado.siguiente_estado.value,
            )
            await session.rollback()
            return None

        conversacion.estado_anterior = estado_origen.value
        conversacion.estado_actual = resultado.siguiente_estado.value
        conversacion.contexto = resultado.contexto
        conversacion.ultima_interaccion = datetime.now(timezone.utc)
        await session.commit()

        if enviar_mensajes is not None and resultado.mensajes_salientes:
            await enviar_mensajes(cliente, resultado.mensajes_salientes)

        return resultado

    @staticmethod
    async def _obtener_o_crear_conversacion(
        session: AsyncSession,
        cliente_id: UUID,
    ) -> Conversacion:
        resultado = await session.exec(
            select(Conversacion).where(Conversacion.cliente_id == cliente_id)
        )
        conversacion = resultado.first()
        if conversacion is not None:
            return conversacion

        conversacion = Conversacion(
            cliente_id=cliente_id,
            estado_actual=EstadoConversacion.IDLE.value,
        )
        session.add(conversacion)
        return conversacion
