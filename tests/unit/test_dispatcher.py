import asyncio
from dataclasses import dataclass, field

import pytest

from src.fsm.dispatcher import (
    DispatcherConversacion,
    HandlerNoRegistradoError,
    MensajeEntrante,
    ResultadoHandler,
    normalizar_mensaje,
)
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente
from src.models.conversacion import Conversacion


@dataclass
class ResultadoFalso:
    conversacion: Conversacion | None

    def first(self) -> Conversacion | None:
        return self.conversacion


@dataclass
class SesionFalsa:
    conversacion: Conversacion | None
    eventos: list[str] = field(default_factory=list)
    agregados: list[Conversacion] = field(default_factory=list)

    async def exec(self, _consulta, params=None):
        if params is not None:
            self.eventos.append("lock")
        return ResultadoFalso(self.conversacion)

    def add(self, conversacion: Conversacion):
        self.agregados.append(conversacion)

    async def commit(self):
        self.eventos.append("commit")

    async def rollback(self):
        self.eventos.append("rollback")


def _cliente() -> Cliente:
    return Cliente(telefono="+5214771234567", nombre="Ana")


def _mensaje() -> MensajeEntrante:
    return MensajeEntrante(tipo="texto", valor="hola", payload={})


def test_normalizar_mensaje_aplana_texto_boton_lista_y_ubicacion():
    texto = normalizar_mensaje({"type": "text", "text": {"body": "10"}})
    boton = normalizar_mensaje(
        {
            "type": "interactive",
            "interactive": {"button_reply": {"id": "hacer_pedido"}},
        }
    )
    lista = normalizar_mensaje(
        {
            "type": "interactive",
            "interactive": {"list_reply": {"id": "confirmar"}},
        }
    )
    ubicacion = normalizar_mensaje(
        {
            "type": "location",
            "location": {"latitude": 21.12, "longitude": -101.68},
        }
    )

    assert (texto.tipo, texto.valor) == ("texto", "10")
    assert (boton.tipo, boton.valor) == ("boton", "hacer_pedido")
    assert (lista.tipo, lista.valor) == ("boton", "confirmar")
    assert (ubicacion.tipo, ubicacion.latitud, ubicacion.longitud) == (
        "ubicacion",
        21.12,
        -101.68,
    )


def test_dispatcher_persiste_antes_de_enviar_respuestas():
    cliente = _cliente()
    conversacion = Conversacion(
        cliente_id=cliente.id,
        estado_actual=EstadoConversacion.IDLE.value,
    )
    sesion = SesionFalsa(conversacion)

    def handler(_mensaje, _contexto, _cliente, _primera_interaccion):
        return ResultadoHandler(
            siguiente_estado=EstadoConversacion.MENU_PRINCIPAL,
            contexto={"paso": "menu"},
            mensajes_salientes=[{"type": "text", "body": "Hola"}],
        )

    async def emisor(_cliente, _mensajes):
        sesion.eventos.append("enviar")

    resultado = asyncio.run(
        DispatcherConversacion({EstadoConversacion.IDLE: handler}).procesar(
            sesion,
            cliente,
            _mensaje(),
            enviar_mensajes=emisor,
        )
    )

    assert resultado is not None
    assert conversacion.estado_anterior == EstadoConversacion.IDLE.value
    assert conversacion.estado_actual == EstadoConversacion.MENU_PRINCIPAL.value
    assert conversacion.contexto == {"paso": "menu"}
    assert sesion.eventos == ["lock", "commit", "enviar"]


def test_transicion_invalida_hace_rollback_y_no_envia():
    cliente = _cliente()
    conversacion = Conversacion(
        cliente_id=cliente.id,
        estado_actual=EstadoConversacion.MENU_PRINCIPAL.value,
    )
    sesion = SesionFalsa(conversacion)

    def handler(_mensaje, _contexto, _cliente, _primera_interaccion):
        return ResultadoHandler(
            siguiente_estado=EstadoConversacion.REVISANDO_RESUMEN,
            contexto={},
            mensajes_salientes=[{"type": "text", "body": "No debe salir"}],
        )

    async def emisor(_cliente, _mensajes):
        sesion.eventos.append("enviar")

    resultado = asyncio.run(
        DispatcherConversacion({EstadoConversacion.MENU_PRINCIPAL: handler}).procesar(
            sesion,
            cliente,
            _mensaje(),
            enviar_mensajes=emisor,
        )
    )

    assert resultado is None
    assert conversacion.estado_actual == EstadoConversacion.MENU_PRINCIPAL.value
    assert sesion.eventos == ["lock", "rollback"]


def test_estado_sin_handler_falla_con_error_claro():
    cliente = _cliente()
    conversacion = Conversacion(
        cliente_id=cliente.id,
        estado_actual=EstadoConversacion.IDLE.value,
    )
    sesion = SesionFalsa(conversacion)

    with pytest.raises(HandlerNoRegistradoError, match="IDLE"):
        asyncio.run(DispatcherConversacion({}).procesar(sesion, cliente, _mensaje()))

    assert sesion.eventos == ["lock", "rollback"]


def test_dispatcher_crea_conversacion_idle_si_el_cliente_no_tenia_una():
    cliente = _cliente()
    sesion = SesionFalsa(conversacion=None)

    def handler(_mensaje, _contexto, _cliente, _primera_interaccion):
        return ResultadoHandler(
            siguiente_estado=EstadoConversacion.MENU_PRINCIPAL,
            contexto={},
            mensajes_salientes=[],
        )

    asyncio.run(
        DispatcherConversacion({EstadoConversacion.IDLE: handler}).procesar(
            sesion,
            cliente,
            _mensaje(),
        )
    )

    assert len(sesion.agregados) == 1
    assert sesion.agregados[0].cliente_id == cliente.id


def test_dispatcher_limpia_el_puntero_del_borrador_al_cancelar():
    cliente = _cliente()
    borrador_id = cliente.id
    conversacion = Conversacion(
        cliente_id=cliente.id,
        estado_actual=EstadoConversacion.CONFIRMANDO_CANCELACION.value,
        pedido_borrador_id=borrador_id,
    )
    sesion = SesionFalsa(conversacion)

    def handler(_mensaje, _contexto, _cliente, _primera_interaccion):
        return ResultadoHandler(
            siguiente_estado=EstadoConversacion.IDLE,
            contexto={"_limpiar_pedido_borrador": True},
            mensajes_salientes=[],
        )

    asyncio.run(
        DispatcherConversacion(
            {EstadoConversacion.CONFIRMANDO_CANCELACION: handler}
        ).procesar(sesion, cliente, _mensaje())
    )

    assert conversacion.estado_actual == EstadoConversacion.IDLE.value
    assert conversacion.pedido_borrador_id is None
    assert conversacion.contexto == {}
