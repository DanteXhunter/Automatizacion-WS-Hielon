"""Reglas de folios, transiciones y confirmación de pedidos."""

from decimal import Decimal
from uuid import uuid4

import pytest

from src.models.direccion import Direccion
from src.models.pedido import EstadoPedido, Pedido
from src.services import pedido_service


class ResultadoEscalar:
    def __init__(self, valor):
        self.valor = valor

    def scalar_one(self):
        return self.valor


class SesionFolio:
    def __init__(self, valor):
        self.valor = valor
        self.parametros = None

    async def exec(self, _consulta, params):
        self.parametros = params
        return ResultadoEscalar(self.valor)


@pytest.mark.asyncio
async def test_folio_usa_anio_y_consecutivo_con_ceros():
    session = SesionFolio(142)
    numero = await pedido_service.generar_numero_orden(session, anio=2026)

    assert numero == "2026-0142"
    assert session.parametros == {"anio": 2026}


@pytest.mark.parametrize(
    ("origen", "destino"),
    [
        (origen, destino)
        for origen, destinos in pedido_service.TRANSICIONES_PEDIDO.items()
        for destino in destinos
    ],
)
def test_cambiar_estado_acepta_todas_las_transiciones_validas(origen, destino):
    pedido = Pedido(cliente_id=uuid4(), estado=origen)

    pedido_service.cambiar_estado(pedido, destino)

    assert pedido.estado == destino


def test_cambiar_estado_repetido_es_noop():
    pedido = Pedido(cliente_id=uuid4(), estado=EstadoPedido.PENDIENTE)

    pedido_service.cambiar_estado(pedido, EstadoPedido.PENDIENTE)

    assert pedido.estado == EstadoPedido.PENDIENTE


@pytest.mark.parametrize(
    ("origen", "destino"),
    [
        (EstadoPedido.BORRADOR, EstadoPedido.ENTREGADO),
        (EstadoPedido.PENDIENTE, EstadoPedido.ENTREGADO),
        (EstadoPedido.PROGRAMADO, EstadoPedido.PENDIENTE),
        (EstadoPedido.EN_RUTA, EstadoPedido.CANCELADO_CLIENTE),
        (EstadoPedido.ENTREGADO, EstadoPedido.PENDIENTE),
        (EstadoPedido.CANCELADO_CLIENTE, EstadoPedido.BORRADOR),
        (EstadoPedido.CANCELADO_NEGOCIO, EstadoPedido.EN_RUTA),
    ],
)
def test_cambiar_estado_rechaza_transiciones_invalidas(origen, destino):
    pedido = Pedido(cliente_id=uuid4(), estado=origen)

    with pytest.raises(pedido_service.TransicionPedidoInvalidaError):
        pedido_service.cambiar_estado(pedido, destino)


class ResultadoPrimero:
    def __init__(self, valor):
        self.valor = valor

    def first(self):
        return self.valor


class SesionConfirmacion:
    def __init__(self, resultados):
        self.resultados = iter(resultados)
        self.flushes = 0

    async def exec(self, _consulta):
        return ResultadoPrimero(next(self.resultados))

    async def flush(self):
        self.flushes += 1


@pytest.mark.asyncio
async def test_confirmacion_recalcula_total_y_deja_pendiente(monkeypatch):
    cliente_id = uuid4()
    pedido = Pedido(id=uuid4(), cliente_id=cliente_id, direccion_id=uuid4())
    direccion = Direccion(id=pedido.direccion_id, cliente_id=cliente_id, texto="Centro")
    session = SesionConfirmacion([pedido, direccion, None])

    async def items(_session, _pedido_id):
        return [(object(), object())]

    async def total(_session, _pedido_id):
        return Decimal("87.50")

    async def folio(_session):
        return "2026-0001"

    monkeypatch.setattr(pedido_service, "listar_items_borrador", items)
    monkeypatch.setattr(pedido_service, "calcular_total_borrador", total)
    monkeypatch.setattr(pedido_service, "generar_numero_orden", folio)

    resultado = await pedido_service.confirmar_pedido(session, cliente_id, pedido.id)

    assert resultado.pedido is pedido
    assert resultado.es_primer_pedido
    assert pedido.numero_orden == "2026-0001"
    assert pedido.total == Decimal("87.50")
    assert pedido.estado == EstadoPedido.PENDIENTE
    assert session.flushes == 1


@pytest.mark.asyncio
async def test_confirmar_dos_veces_no_genera_otro_folio(monkeypatch):
    cliente_id = uuid4()
    pedido = Pedido(
        id=uuid4(),
        cliente_id=cliente_id,
        estado=EstadoPedido.PENDIENTE,
        numero_orden="2026-0007",
    )
    session = SesionConfirmacion([pedido])

    async def no_generar(_session):
        raise AssertionError("No debe reservarse otro folio")

    monkeypatch.setattr(pedido_service, "generar_numero_orden", no_generar)
    resultado = await pedido_service.confirmar_pedido(session, cliente_id, pedido.id)

    assert resultado.ya_estaba_confirmado
    assert resultado.pedido.numero_orden == "2026-0007"
