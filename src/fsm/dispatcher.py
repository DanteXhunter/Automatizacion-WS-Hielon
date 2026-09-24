"""Enrutamiento transaccional de mensajes hacia handlers de conversación."""

import inspect
import logging
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.fsm.states import (
    TRANSICIONES_ATRAS,
    EstadoConversacion,
    es_transicion_valida,
)
from src.models.cliente import Cliente
from src.models.conversacion import Conversacion
from src.services.locks import bloqueo_por_cliente
from src.services.pedido_service import obtener_ultimo_pedido_activo

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


HandlerConversacion = Callable[..., ResultadoHandler | Awaitable[ResultadoHandler]]
EmisorMensajes = Callable[[Cliente, list[dict[str, Any]]], Awaitable[None]]
NotificadorHandoff = Callable[[Cliente, str, MensajeEntrante], Awaitable[None]]


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
        notificar_handoff: NotificadorHandoff | None = None,
    ) -> ResultadoHandler | None:
        """Serializa por cliente y persiste el estado antes de enviar respuestas."""
        nuevo_handoff = False
        motivo_handoff = ""
        async with bloqueo_por_cliente(session, cliente.id):
            conversacion, primera_interaccion = (
                await self._obtener_o_crear_conversacion(session, cliente.id)
            )
            estado_origen = EstadoConversacion(conversacion.estado_actual)
            if estado_origen == EstadoConversacion.EN_ASESOR_HUMANO:
                conversacion.ultima_interaccion = datetime.now(timezone.utc)
                await session.commit()
                return ResultadoHandler(
                    EstadoConversacion.EN_ASESOR_HUMANO,
                    conversacion.contexto.copy(),
                    [],
                )

            handler = self._handlers.get(estado_origen)
            if handler is None:
                raise HandlerNoRegistradoError(
                    f"No hay handler registrado para el estado {estado_origen.value}."
                )

            contexto_handler = conversacion.contexto.copy()
            if (
                estado_origen == EstadoConversacion.MENU_PRINCIPAL
                and mensaje.tipo == "boton"
                and mensaje.valor == "consultar"
            ):
                pedido = await obtener_ultimo_pedido_activo(session, cliente.id)
                if pedido is not None:
                    contexto_handler["_pedido_activo"] = {
                        "numero_orden": pedido.numero_orden,
                        "estado": pedido.estado.value,
                    }

            resultado_atras = await self._resolver_volver(
                session,
                cliente,
                conversacion,
                estado_origen,
                mensaje,
                contexto_handler,
            )
            if resultado_atras is not None:
                resultado = resultado_atras
            else:
                parametros = inspect.signature(handler).parameters
                argumentos = (mensaje, contexto_handler, cliente, primera_interaccion)
                if "session" in parametros:
                    kwargs: dict[str, Any] = {"session": session}
                    if "pedido_borrador_id" in parametros:
                        kwargs["pedido_borrador_id"] = conversacion.pedido_borrador_id
                    respuesta = handler(*argumentos, **kwargs)
                else:
                    respuesta = handler(*argumentos)
                resultado = (
                    await respuesta if inspect.isawaitable(respuesta) else respuesta
                )
            if not es_transicion_valida(estado_origen, resultado.siguiente_estado):
                logger.warning(
                    "Transición inválida descartada | cliente_id=%s origen=%s destino=%s",
                    cliente.id,
                    estado_origen.value,
                    resultado.siguiente_estado.value,
                )
                await session.rollback()
                return None

            nuevo_handoff = (
                estado_origen != EstadoConversacion.EN_ASESOR_HUMANO
                and resultado.siguiente_estado == EstadoConversacion.EN_ASESOR_HUMANO
            )
            if nuevo_handoff:
                motivo_handoff = str(
                    resultado.contexto.get(
                        "handoff_motivo",
                        "Escalamiento automático",
                    )
                )
                resultado.contexto["handoff_motivo"] = motivo_handoff
                resultado.contexto["handoff_desde"] = estado_origen.value
                resultado.contexto["handoff_iniciado_en"] = datetime.now(
                    timezone.utc
                ).isoformat()

            conversacion.estado_anterior = estado_origen.value
            conversacion.estado_actual = resultado.siguiente_estado.value
            conversacion.contexto = resultado.contexto
            limpiar_borrador = bool(
                conversacion.contexto.pop("_limpiar_pedido_borrador", False)
            )
            borrador_id = resultado.contexto.get("pedido_borrador_id")
            if limpiar_borrador:
                conversacion.pedido_borrador_id = None
            elif isinstance(borrador_id, str):
                try:
                    conversacion.pedido_borrador_id = UUID(borrador_id)
                except ValueError:
                    conversacion.pedido_borrador_id = None
            conversacion.ultima_interaccion = datetime.now(timezone.utc)
            await session.commit()

        if nuevo_handoff and notificar_handoff is not None:
            try:
                await notificar_handoff(cliente, motivo_handoff, mensaje)
            except Exception:
                logger.exception(
                    "La notificación de handoff falló sin revertir el estado | "
                    "cliente_id=%s",
                    cliente.id,
                )

        if enviar_mensajes is not None and resultado.mensajes_salientes:
            await enviar_mensajes(cliente, resultado.mensajes_salientes)

        return resultado

    @staticmethod
    async def _resolver_volver(
        session: AsyncSession,
        cliente: Cliente,
        conversacion: Conversacion,
        estado_origen: EstadoConversacion,
        mensaje: MensajeEntrante,
        contexto: dict[str, Any],
    ) -> ResultadoHandler | None:
        """Resuelve navegación atrás y sus limpiezas antes de invocar handlers."""
        if mensaje.tipo != "boton" or mensaje.valor != "volver":
            return None
        destino = TRANSICIONES_ATRAS.get(estado_origen)
        if destino is None:
            return ResultadoHandler(estado_origen, contexto, [])

        # Los imports locales evitan ciclos: los handlers importan los tipos
        # MensajeEntrante y ResultadoHandler de este mismo módulo.
        from src.fsm.handlers.menu_principal import crear_menu, crear_selector_productos
        from src.fsm.handlers.pedido import (
            crear_mensaje_carrito,
            crear_pregunta_cantidad,
        )
        from src.fsm.handlers.pedido_finalizacion import crear_mensaje_resumen
        from src.services.pedido_service import (
            calcular_total_borrador,
            eliminar_item_borrador,
            listar_items_borrador,
            listar_productos_activos,
            obtener_borrador,
        )

        if estado_origen == EstadoConversacion.SELECCIONANDO_PRODUCTO:
            contexto.pop("producto_actual", None)
            return ResultadoHandler(destino, contexto, [crear_menu()])

        if estado_origen == EstadoConversacion.CAPTURANDO_CANTIDAD:
            contexto.pop("producto_actual", None)
            productos = await listar_productos_activos(session)
            mensajes = (
                [crear_selector_productos(productos)]
                if productos
                else [{"type": "text", "body": "No hay productos disponibles."}]
            )
            return ResultadoHandler(destino, contexto, mensajes)

        if estado_origen == EstadoConversacion.AGREGAR_MAS_O_CONTINUAR:
            pedido = await obtener_borrador(
                session,
                cliente.id,
                conversacion.pedido_borrador_id,
            )
            if pedido is not None:
                items = await listar_items_borrador(session, pedido.id)
                ultimo_id = _uuid_opcional(contexto.get("ultimo_item_id"))
                ultimo = next(
                    (
                        (item, producto)
                        for item, producto in items
                        if item.id == ultimo_id
                    ),
                    None,
                )
                if ultimo is not None:
                    item, producto = ultimo
                    await eliminar_item_borrador(session, pedido, item.id)
                    contexto["producto_actual"] = str(producto.id)
                    contexto.pop("ultimo_item_id", None)
                    return ResultadoHandler(
                        destino,
                        contexto,
                        [crear_pregunta_cantidad(producto)],
                    )

            productos = await listar_productos_activos(session)
            contexto.pop("ultimo_item_id", None)
            return ResultadoHandler(
                EstadoConversacion.SELECCIONANDO_PRODUCTO,
                contexto,
                (
                    [crear_selector_productos(productos)]
                    if productos
                    else [{"type": "text", "body": "No hay productos disponibles."}]
                ),
            )

        if estado_origen == EstadoConversacion.CAPTURANDO_DIRECCION:
            pedido = await obtener_borrador(
                session,
                cliente.id,
                conversacion.pedido_borrador_id,
            )
            if pedido is None:
                return ResultadoHandler(
                    destino,
                    contexto,
                    [{"type": "text", "body": "Regresamos a tu carrito."}],
                )
            items = await listar_items_borrador(session, pedido.id)
            total = await calcular_total_borrador(session, pedido.id)
            return ResultadoHandler(
                destino,
                contexto,
                [crear_mensaje_carrito(items, total)],
            )

        return ResultadoHandler(
            destino,
            contexto,
            [
                await crear_mensaje_resumen(
                    session,
                    cliente,
                    conversacion.pedido_borrador_id,
                )
            ],
        )

    @staticmethod
    async def _obtener_o_crear_conversacion(
        session: AsyncSession,
        cliente_id: UUID,
    ) -> tuple[Conversacion, bool]:
        resultado = await session.exec(
            select(Conversacion).where(Conversacion.cliente_id == cliente_id)
        )
        conversacion = resultado.first()
        if conversacion is not None:
            return conversacion, False

        conversacion = Conversacion(
            cliente_id=cliente_id,
            estado_actual=EstadoConversacion.IDLE.value,
        )
        session.add(conversacion)
        return conversacion, True


def _uuid_opcional(valor: Any) -> UUID | None:
    """Convierte un UUID persistido en JSON sin propagar datos corruptos."""
    if not isinstance(valor, str):
        return None
    try:
        return UUID(valor)
    except ValueError:
        return None
