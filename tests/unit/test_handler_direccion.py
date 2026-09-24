"""Pruebas de captura, reutilización y validación de direcciones."""

from decimal import Decimal
from uuid import uuid4

import pytest

from src.fsm.dispatcher import MensajeEntrante
from src.fsm.handlers import direccion as handler_direccion
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente
from src.models.direccion import Direccion
from src.models.pedido import Pedido

CLIENTE = Cliente(id=uuid4(), telefono="+5214771234567")
PEDIDO = Pedido(id=uuid4(), cliente_id=CLIENTE.id)


class SesionFalsa:
    async def exec(self, _consulta):
        raise AssertionError("La consulta debía reemplazarse en esta prueba unitaria")


def _mensaje(tipo: str, valor=None, payload=None, latitud=None, longitud=None):
    return MensajeEntrante(
        tipo=tipo,
        valor=valor,
        payload=payload or {},
        latitud=latitud,
        longitud=longitud,
    )


@pytest.mark.asyncio
async def test_cliente_con_direccion_previa_puede_reutilizarla(monkeypatch):
    anterior = Direccion(
        id=uuid4(),
        cliente_id=CLIENTE.id,
        texto="Calle del Sol 123, Centro",
        es_ultima_usada=True,
    )
    pedido = Pedido(id=PEDIDO.id, cliente_id=CLIENTE.id)
    marcada = []

    async def ultima(_session, _cliente_id):
        return anterior

    async def marcar(_session, _cliente_id, direccion):
        marcada.append(direccion.id)

    async def borrador(_session, _cliente_id, _borrador_id):
        return pedido

    async def resumen(_session, _cliente, _pedido_id):
        return {"type": "text", "body": "Resumen"}

    monkeypatch.setattr(handler_direccion, "obtener_ultima_direccion", ultima)
    monkeypatch.setattr(handler_direccion, "marcar_ultima_direccion", marcar)
    monkeypatch.setattr(handler_direccion, "obtener_borrador", borrador)
    monkeypatch.setattr(handler_direccion, "crear_mensaje_resumen", resumen)

    prompt = await handler_direccion.mensaje_inicial_direccion(
        SesionFalsa(), CLIENTE.id
    )
    resultado = await handler_direccion.atender_captura_direccion(
        _mensaje("boton", "usar_esta"),
        {"pedido_borrador_id": str(PEDIDO.id)},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=PEDIDO.id,
    )

    assert "dirección de siempre" in prompt["interactive"]["body"]["text"]
    assert prompt["interactive"]["action"]["buttons"][0]["reply"]["id"] == "usar_esta"
    assert marcada == [anterior.id]
    assert pedido.direccion_id == anterior.id
    assert resultado.siguiente_estado == EstadoConversacion.REVISANDO_RESUMEN


@pytest.mark.asyncio
async def test_direccion_texto_guarda_y_actualiza_borrador(monkeypatch):
    nueva = Direccion(
        id=uuid4(), cliente_id=CLIENTE.id, texto="Av. Central 42, San Juan"
    )
    pedido = Pedido(id=PEDIDO.id, cliente_id=CLIENTE.id)
    guardado = []

    async def guardar(_session, cliente_id, **campos):
        guardado.append((cliente_id, campos))
        return nueva

    async def borrador(_session, _cliente_id, _borrador_id):
        return pedido

    async def resumen(_session, _cliente, _pedido_id):
        return {"type": "text", "body": "Resumen"}

    monkeypatch.setattr(handler_direccion, "guardar_direccion", guardar)
    monkeypatch.setattr(handler_direccion, "obtener_borrador", borrador)
    monkeypatch.setattr(handler_direccion, "crear_mensaje_resumen", resumen)
    resultado = await handler_direccion.atender_captura_direccion(
        _mensaje("texto", "Av. Central 42, San Juan"),
        {},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=PEDIDO.id,
    )

    assert guardado == [(CLIENTE.id, {"texto": "Av. Central 42, San Juan"})]
    assert pedido.direccion_id == nueva.id
    assert resultado.siguiente_estado == EstadoConversacion.REVISANDO_RESUMEN


@pytest.mark.asyncio
async def test_ubicacion_guarda_coordenadas_y_texto_del_payload(monkeypatch):
    async def guardar(_session, _cliente_id, **campos):
        assert campos == {
            "texto": "Blvd. Hidalgo 210",
            "latitud": Decimal("21.12"),
            "longitud": Decimal("-101.68"),
        }
        return Direccion(id=uuid4(), cliente_id=CLIENTE.id, **campos)

    async def borrador(_session, _cliente_id, _borrador_id):
        return PEDIDO

    async def resumen(_session, _cliente, _pedido_id):
        return {"type": "text", "body": "Resumen"}

    monkeypatch.setattr(handler_direccion, "guardar_direccion", guardar)
    monkeypatch.setattr(handler_direccion, "obtener_borrador", borrador)
    monkeypatch.setattr(handler_direccion, "crear_mensaje_resumen", resumen)
    resultado = await handler_direccion.atender_captura_direccion(
        _mensaje(
            "ubicacion",
            payload={"location": {"address": "Blvd. Hidalgo 210"}},
            latitud=21.12,
            longitud=-101.68,
        ),
        {},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=PEDIDO.id,
    )

    assert resultado.siguiente_estado == EstadoConversacion.REVISANDO_RESUMEN


@pytest.mark.asyncio
async def test_texto_corto_se_rechaza_y_volver_regresa_al_carrito():
    corto = await handler_direccion.atender_captura_direccion(
        _mensaje("texto", "123"),
        {},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=PEDIDO.id,
    )
    atras = await handler_direccion.atender_captura_direccion(
        _mensaje("boton", "volver"),
        {},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=PEDIDO.id,
    )

    assert corto.siguiente_estado == EstadoConversacion.CAPTURANDO_DIRECCION
    assert "muy corta" in corto.mensajes_salientes[0]["body"]
    assert atras.siguiente_estado == EstadoConversacion.AGREGAR_MAS_O_CONTINUAR
