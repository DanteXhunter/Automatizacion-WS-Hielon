"""Pruebas de resumen, modificación y cancelación del borrador."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from src.fsm.dispatcher import MensajeEntrante
from src.fsm.handlers import pedido_finalizacion as finalizacion
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente
from src.models.direccion import Direccion
from src.models.pedido import EstadoPedido, Pedido
from src.models.producto import Producto

CLIENTE = Cliente(id=uuid4(), telefono="+5214771234567")
PEDIDO = Pedido(id=uuid4(), cliente_id=CLIENTE.id)


class ResultadoFalso:
    def first(self):
        return Direccion(
            id=PEDIDO.direccion_id or uuid4(),
            cliente_id=CLIENTE.id,
            texto="Calle Norte 25, Centro",
        )


class SesionFalsa:
    async def exec(self, _consulta):
        return ResultadoFalso()


def _mensaje(valor, tipo="boton"):
    return MensajeEntrante(tipo=tipo, valor=valor, payload={})


@pytest.mark.asyncio
async def test_resumen_usa_total_de_items_y_lista_las_cuatro_acciones(monkeypatch):
    producto = Producto(
        id=uuid4(), nombre="Bolsa 5 kg", peso_kg=Decimal(5), precio=Decimal("12.50")
    )
    item = type(
        "Item",
        (),
        {
            "cantidad": 3,
            "subtotal": Decimal("37.50"),
            "precio_unitario": Decimal("12.50"),
        },
    )()
    PEDIDO.direccion_id = uuid4()
    monkeypatch.setattr(
        finalizacion, "obtener_borrador", lambda *_args: _async_value(PEDIDO)
    )
    monkeypatch.setattr(
        finalizacion,
        "listar_items_borrador",
        lambda *_args: _async_value([(item, producto)]),
    )
    monkeypatch.setattr(
        finalizacion,
        "calcular_total_borrador",
        lambda *_args: _async_value(Decimal("37.50")),
    )
    monkeypatch.setattr(finalizacion, "debe_sugerir_entrega_manana", lambda: True)

    mensaje = await finalizacion.crear_mensaje_resumen(
        SesionFalsa(), CLIENTE, PEDIDO.id
    )
    interactivo = mensaje["interactive"]
    filas = interactivo["action"]["sections"][0]["rows"]
    texto = interactivo["body"]["text"]

    assert interactivo["type"] == "list"
    assert [fila["id"] for fila in filas] == [
        "confirmar",
        "modificar",
        "cancelar",
        "asesor",
    ]
    assert "3 x Bolsa 5 kg" in texto
    assert "Calle Norte 25" in texto
    assert "Total: $37.50" in texto
    assert "no incluyen IVA ni envío" in texto
    assert texto.startswith("Ya pasó nuestro horario de corte de las 14:00")


def test_sugerencia_de_manana_solo_aplica_despues_del_corte_en_dia_habil(
    monkeypatch,
):
    zona = ZoneInfo("America/Mexico_City")

    monkeypatch.setattr(
        finalizacion,
        "ahora_local",
        lambda: datetime(2026, 9, 21, 13, 59, tzinfo=zona),
    )
    assert finalizacion.debe_sugerir_entrega_manana() is False

    monkeypatch.setattr(
        finalizacion,
        "ahora_local",
        lambda: datetime(2026, 9, 21, 14, 1, tzinfo=zona),
    )
    assert finalizacion.debe_sugerir_entrega_manana() is True

    monkeypatch.setattr(
        finalizacion,
        "ahora_local",
        lambda: datetime(2026, 9, 27, 14, 1, tzinfo=zona),
    )
    assert finalizacion.debe_sugerir_entrega_manana() is False


def _async_value(valor):
    async def resolver(*_args):
        return valor

    return resolver()


@pytest.mark.asyncio
async def test_acciones_no_terminales_del_resumen_enrutan_a_sus_estados():
    esperados = {
        "modificar": EstadoConversacion.SELECCIONANDO_MODIFICACION,
        "cancelar": EstadoConversacion.CONFIRMANDO_CANCELACION,
        "asesor": EstadoConversacion.EN_ASESOR_HUMANO,
    }
    for boton, estado in esperados.items():
        resultado = await finalizacion.atender_revision_resumen(
            _mensaje(boton),
            {"pedido_borrador_id": str(PEDIDO.id)},
            CLIENTE,
            False,
            session=SesionFalsa(),
            pedido_borrador_id=PEDIDO.id,
        )
        assert resultado.siguiente_estado == estado


@pytest.mark.asyncio
async def test_hablar_con_asesor_conserva_borrador_y_confirma_al_cliente():
    contexto = {"pedido_borrador_id": str(PEDIDO.id), "carrito": "intacto"}

    resultado = await finalizacion.atender_revision_resumen(
        _mensaje("asesor"),
        contexto,
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=PEDIDO.id,
    )

    assert resultado.siguiente_estado == EstadoConversacion.EN_ASESOR_HUMANO
    assert resultado.contexto["pedido_borrador_id"] == str(PEDIDO.id)
    assert resultado.contexto["carrito"] == "intacto"
    assert resultado.contexto["handoff_motivo"] == "Solicitud del cliente"
    assert "en un momento" in resultado.mensajes_salientes[0]["body"]


@pytest.mark.asyncio
async def test_confirmar_limpia_borrador_y_muestra_folio(monkeypatch):
    pedido = Pedido(
        id=PEDIDO.id,
        cliente_id=CLIENTE.id,
        estado=EstadoPedido.PENDIENTE,
        numero_orden="2026-0142",
        total=Decimal("37.50"),
    )

    async def confirmar(_session, _cliente_id, _pedido_id):
        from src.services.pedido_service import ResultadoConfirmacionPedido

        return ResultadoConfirmacionPedido(pedido=pedido, es_primer_pedido=True)

    monkeypatch.setattr(finalizacion, "confirmar_pedido", confirmar)
    resultado = await finalizacion.atender_revision_resumen(
        _mensaje("confirmar"),
        {"pedido_borrador_id": str(PEDIDO.id)},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=PEDIDO.id,
    )

    assert resultado.siguiente_estado == EstadoConversacion.IDLE
    assert resultado.contexto == {"_limpiar_pedido_borrador": True}
    assert "2026-0142" in resultado.mensajes_salientes[0]["body"]
    assert "$37.50" in resultado.mensajes_salientes[0]["body"]
    assert "contra entrega" in resultado.mensajes_salientes[0]["body"]


@pytest.mark.asyncio
async def test_modificar_productos_pide_confirmacion_antes_de_vaciar(monkeypatch):
    borrados = []
    producto = Producto(
        id=uuid4(), nombre="Bolsa 3 kg", peso_kg=Decimal(3), precio=Decimal(0)
    )

    async def vaciar(_session, pedido):
        borrados.append(pedido.id)

    async def listar(_session):
        return [producto]

    monkeypatch.setattr(finalizacion, "vaciar_items_borrador", vaciar)
    monkeypatch.setattr(
        finalizacion, "obtener_borrador", lambda *_args: _async_value(PEDIDO)
    )
    monkeypatch.setattr(finalizacion, "listar_productos_activos", listar)

    advertencia = await finalizacion.atender_seleccion_modificacion(
        _mensaje("productos"),
        {"pedido_borrador_id": str(PEDIDO.id)},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=PEDIDO.id,
    )
    assert advertencia.siguiente_estado == EstadoConversacion.SELECCIONANDO_MODIFICACION
    assert not borrados
    assert (
        "se conservará la dirección"
        in advertencia.mensajes_salientes[0]["interactive"]["body"]["text"]
    )

    confirmado = await finalizacion.atender_seleccion_modificacion(
        _mensaje("si_rehacer"),
        {
            "confirmar_recaptura_productos": True,
            "pedido_borrador_id": str(PEDIDO.id),
        },
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=PEDIDO.id,
    )
    assert borrados == [PEDIDO.id]
    assert confirmado.siguiente_estado == EstadoConversacion.SELECCIONANDO_PRODUCTO
    assert confirmado.contexto["pedido_borrador_id"] == str(PEDIDO.id)


@pytest.mark.asyncio
async def test_cancelar_marca_pedido_y_pide_limpiar_el_borrador(monkeypatch):
    pedido = Pedido(id=PEDIDO.id, cliente_id=CLIENTE.id, estado=EstadoPedido.BORRADOR)

    async def obtener(_session, _cliente_id, _borrador_id):
        return pedido

    monkeypatch.setattr(finalizacion, "obtener_borrador", obtener)
    resultado = await finalizacion.atender_confirmacion_cancelacion(
        _mensaje("si_cancelar"),
        {"pedido_borrador_id": str(pedido.id)},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=pedido.id,
    )

    assert pedido.estado == EstadoPedido.CANCELADO_CLIENTE
    assert resultado.siguiente_estado == EstadoConversacion.IDLE
    assert resultado.contexto["_limpiar_pedido_borrador"] is True
    assert "cancelamos tu pedido" in resultado.mensajes_salientes[0]["body"]


@pytest.mark.asyncio
async def test_respuesta_distinta_a_confirmar_cancelacion_no_cancela(monkeypatch):
    pedido = Pedido(id=PEDIDO.id, cliente_id=CLIENTE.id, estado=EstadoPedido.BORRADOR)

    async def obtener(_session, _cliente_id, _borrador_id):
        return pedido

    monkeypatch.setattr(finalizacion, "obtener_borrador", obtener)
    resultado = await finalizacion.atender_confirmacion_cancelacion(
        _mensaje("quizá"),
        {},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=pedido.id,
    )

    assert pedido.estado == EstadoPedido.BORRADOR
    assert resultado.siguiente_estado == EstadoConversacion.CONFIRMANDO_CANCELACION
    assert resultado.mensajes_salientes[0]["interactive"]["body"]["text"].startswith(
        "¿Seguro"
    )
