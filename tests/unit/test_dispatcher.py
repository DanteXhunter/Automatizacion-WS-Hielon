import asyncio
from dataclasses import dataclass, field
from decimal import Decimal
from types import SimpleNamespace

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
from src.models.pedido import Pedido
from src.models.producto import Producto
from src.services import pedido_service


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


def test_volver_se_intercepta_sin_invocar_el_handler_del_estado():
    cliente = _cliente()
    conversacion = Conversacion(
        cliente_id=cliente.id,
        estado_actual=EstadoConversacion.SELECCIONANDO_PRODUCTO.value,
        contexto={"producto_actual": str(cliente.id)},
    )
    sesion = SesionFalsa(conversacion)

    def handler(*_args):
        raise AssertionError("El dispatcher debía interceptar Volver")

    resultado = asyncio.run(
        DispatcherConversacion(
            {EstadoConversacion.SELECCIONANDO_PRODUCTO: handler}
        ).procesar(
            sesion,
            cliente,
            MensajeEntrante(tipo="boton", valor="volver", payload={}),
        )
    )

    assert resultado is not None
    assert resultado.siguiente_estado == EstadoConversacion.MENU_PRINCIPAL
    assert "producto_actual" not in resultado.contexto


def test_volver_dos_veces_limpia_item_y_regresa_a_productos(monkeypatch):
    cliente = _cliente()
    pedido = Pedido(id=cliente.id, cliente_id=cliente.id)
    producto = Producto(
        nombre="Bolsa 5 kg",
        peso_kg=Decimal(5),
        precio=Decimal("12.50"),
    )
    item = SimpleNamespace(id=producto.id)
    conversacion = Conversacion(
        cliente_id=cliente.id,
        estado_actual=EstadoConversacion.AGREGAR_MAS_O_CONTINUAR.value,
        pedido_borrador_id=pedido.id,
        contexto={"ultimo_item_id": str(item.id)},
    )
    sesion = SesionFalsa(conversacion)
    eliminados = []

    async def obtener(_session, _cliente_id, _pedido_id):
        return pedido

    async def listar_items(_session, _pedido_id):
        return [(item, producto)]

    async def eliminar(_session, _pedido, item_id):
        eliminados.append(item_id)
        return True

    async def listar_productos(_session):
        return [producto]

    monkeypatch.setattr(pedido_service, "obtener_borrador", obtener)
    monkeypatch.setattr(pedido_service, "listar_items_borrador", listar_items)
    monkeypatch.setattr(pedido_service, "eliminar_item_borrador", eliminar)
    monkeypatch.setattr(pedido_service, "listar_productos_activos", listar_productos)

    def handler(*_args):
        raise AssertionError("El dispatcher debía interceptar Volver")

    dispatcher = DispatcherConversacion(
        {
            EstadoConversacion.AGREGAR_MAS_O_CONTINUAR: handler,
            EstadoConversacion.CAPTURANDO_CANTIDAD: handler,
        }
    )
    mensaje = MensajeEntrante(tipo="boton", valor="volver", payload={})

    primero = asyncio.run(dispatcher.procesar(sesion, cliente, mensaje))
    segundo = asyncio.run(dispatcher.procesar(sesion, cliente, mensaje))

    assert primero is not None and segundo is not None
    assert eliminados == [item.id]
    assert primero.siguiente_estado == EstadoConversacion.CAPTURANDO_CANTIDAD
    assert segundo.siguiente_estado == EstadoConversacion.SELECCIONANDO_PRODUCTO
    assert "producto_actual" not in segundo.contexto


def test_volver_en_estado_sin_regreso_se_ignora_sin_mensaje():
    cliente = _cliente()
    conversacion = Conversacion(
        cliente_id=cliente.id,
        estado_actual=EstadoConversacion.MENU_PRINCIPAL.value,
    )
    sesion = SesionFalsa(conversacion)

    def handler(*_args):
        raise AssertionError("Un Volver no admitido no debe llegar al handler")

    resultado = asyncio.run(
        DispatcherConversacion({EstadoConversacion.MENU_PRINCIPAL: handler}).procesar(
            sesion,
            cliente,
            MensajeEntrante(tipo="boton", valor="volver", payload={}),
        )
    )

    assert resultado is not None
    assert resultado.siguiente_estado == EstadoConversacion.MENU_PRINCIPAL
    assert resultado.mensajes_salientes == []
