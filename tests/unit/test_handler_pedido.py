"""Validación del flujo de selección, cantidades y operaciones del carrito."""

from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from src.fsm.dispatcher import MensajeEntrante
from src.fsm.handlers import pedido as handler_pedido
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente
from src.models.pedido import Pedido
from src.models.producto import Producto

CLIENTE = Cliente(id=uuid4(), telefono="+5214771234567")
PRODUCTO = Producto(
    id=uuid4(),
    nombre="Bolsa 5 kg",
    peso_kg=Decimal(5),
    precio=Decimal("12.50"),
    activo=True,
)


class SesionFalsa:
    async def exec(self, _consulta):
        raise AssertionError("La consulta debía reemplazarse en esta prueba unitaria")


def _mensaje(valor: str, tipo: str = "texto") -> MensajeEntrante:
    return MensajeEntrante(tipo=tipo, valor=valor, payload={})


@pytest.mark.asyncio
async def test_selecciona_producto_por_uuid_y_guarda_en_contexto(monkeypatch):
    async def obtener_producto(_session, producto_id):
        assert producto_id == PRODUCTO.id
        return PRODUCTO

    monkeypatch.setattr(handler_pedido, "obtener_producto_activo", obtener_producto)
    resultado = await handler_pedido.atender_seleccion_producto(
        _mensaje(str(PRODUCTO.id), "boton"), {}, CLIENTE, False, session=SesionFalsa()
    )

    assert resultado.siguiente_estado == EstadoConversacion.CAPTURANDO_CANTIDAD
    assert resultado.contexto["producto_actual"] == str(PRODUCTO.id)
    assert (
        "¿Cuántas bolsas"
        in resultado.mensajes_salientes[0]["interactive"]["body"]["text"]
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("entrada", ["10 kg", "diez", "0", "-1", "1.5", "999999"])
async def test_rechaza_cantidades_que_no_son_enteros_positivos_acotados(
    monkeypatch, entrada
):
    async def obtener_producto(_session, _producto_id):
        return PRODUCTO

    monkeypatch.setattr(handler_pedido, "obtener_producto_activo", obtener_producto)
    resultado = await handler_pedido.atender_captura_cantidad(
        _mensaje(entrada),
        {"producto_actual": str(PRODUCTO.id)},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=None,
    )

    assert resultado.siguiente_estado == EstadoConversacion.CAPTURANDO_CANTIDAD
    assert len(resultado.mensajes_salientes) == 1
    texto = resultado.mensajes_salientes[0]["interactive"]["body"]["text"]
    assert "número de bolsas" in texto
    assert "Por ejemplo: 10" in texto


@pytest.mark.asyncio
async def test_cantidad_valida_crea_item_y_muestra_carrito_desde_totales_db(
    monkeypatch,
):
    pedido = Pedido(id=uuid4(), cliente_id=CLIENTE.id)
    item = SimpleNamespace(
        id=uuid4(),
        cantidad=3,
        subtotal=Decimal("37.50"),
        precio_unitario=Decimal("12.50"),
    )
    guardado = {}

    async def obtener_producto(_session, _producto_id):
        return PRODUCTO

    async def obtener_o_crear(_session, cliente_id, borrador_id):
        assert cliente_id == CLIENTE.id
        assert borrador_id is None
        return pedido

    async def agregar(_session, _pedido, producto, cantidad):
        guardado.update(producto=producto, cantidad=cantidad)
        return item

    async def listar(_session, pedido_id):
        assert pedido_id == pedido.id
        return [(item, PRODUCTO)]

    async def total(_session, pedido_id):
        assert pedido_id == pedido.id
        return Decimal("37.50")

    monkeypatch.setattr(handler_pedido, "obtener_producto_activo", obtener_producto)
    monkeypatch.setattr(handler_pedido, "obtener_o_crear_borrador", obtener_o_crear)
    monkeypatch.setattr(handler_pedido, "agregar_item_borrador", agregar)
    monkeypatch.setattr(handler_pedido, "listar_items_borrador", listar)
    monkeypatch.setattr(handler_pedido, "calcular_total_borrador", total)

    resultado = await handler_pedido.atender_captura_cantidad(
        _mensaje("3"),
        {"producto_actual": str(PRODUCTO.id)},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=None,
    )

    assert guardado == {"producto": PRODUCTO, "cantidad": 3}
    assert resultado.siguiente_estado == EstadoConversacion.AGREGAR_MAS_O_CONTINUAR
    assert resultado.contexto["pedido_borrador_id"] == str(pedido.id)
    assert (
        "Total parcial: $37.50"
        in resultado.mensajes_salientes[0]["interactive"]["body"]["text"]
    )
    assert "producto_actual" not in resultado.contexto


@pytest.mark.asyncio
async def test_volver_desde_carrito_elimina_el_ultimo_item_y_reabre_su_producto(
    monkeypatch,
):
    pedido = Pedido(id=uuid4(), cliente_id=CLIENTE.id)
    item = SimpleNamespace(
        id=uuid4(),
        cantidad=2,
        subtotal=Decimal("25.00"),
        precio_unitario=Decimal("12.50"),
    )
    eliminados = []

    async def obtener_o_crear(_session, _cliente_id, _borrador_id):
        return pedido

    async def listar(_session, _pedido_id):
        return [(item, PRODUCTO)]

    async def eliminar(_session, _pedido, item_id):
        eliminados.append(item_id)
        return True

    monkeypatch.setattr(handler_pedido, "obtener_o_crear_borrador", obtener_o_crear)
    monkeypatch.setattr(handler_pedido, "listar_items_borrador", listar)
    monkeypatch.setattr(handler_pedido, "eliminar_item_borrador", eliminar)
    resultado = await handler_pedido.atender_carrito(
        _mensaje("volver", "boton"),
        {"ultimo_item_id": str(item.id)},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=pedido.id,
    )

    assert eliminados == [item.id]
    assert resultado.siguiente_estado == EstadoConversacion.CAPTURANDO_CANTIDAD
    assert resultado.contexto["producto_actual"] == str(PRODUCTO.id)


@pytest.mark.asyncio
async def test_carrito_muestra_tres_items_y_recalcula_el_total(monkeypatch):
    pedido = Pedido(id=uuid4(), cliente_id=CLIENTE.id)
    productos = [
        PRODUCTO,
        Producto(
            id=uuid4(),
            nombre="Bolsa 3 kg",
            peso_kg=Decimal(3),
            precio=Decimal("8.00"),
        ),
        Producto(
            id=uuid4(),
            nombre="Bolsa 10 kg",
            peso_kg=Decimal(10),
            precio=Decimal("20.00"),
        ),
    ]
    items = [
        (
            SimpleNamespace(
                cantidad=2, subtotal=Decimal("25.00"), precio_unitario=Decimal("12.50")
            ),
            productos[0],
        ),
        (
            SimpleNamespace(
                cantidad=1, subtotal=Decimal("8.00"), precio_unitario=Decimal("8.00")
            ),
            productos[1],
        ),
        (
            SimpleNamespace(
                cantidad=3, subtotal=Decimal("60.00"), precio_unitario=Decimal("20.00")
            ),
            productos[2],
        ),
    ]

    async def obtener_o_crear(_session, _cliente_id, _borrador_id):
        return pedido

    async def listar(_session, pedido_id):
        assert pedido_id == pedido.id
        return items

    async def total(_session, pedido_id):
        assert pedido_id == pedido.id
        return Decimal("93.00")

    monkeypatch.setattr(handler_pedido, "obtener_o_crear_borrador", obtener_o_crear)
    monkeypatch.setattr(handler_pedido, "listar_items_borrador", listar)
    monkeypatch.setattr(handler_pedido, "calcular_total_borrador", total)
    resultado = await handler_pedido.atender_carrito(
        _mensaje("desconocido", "texto"),
        {},
        CLIENTE,
        False,
        session=SesionFalsa(),
        pedido_borrador_id=pedido.id,
    )

    texto = resultado.mensajes_salientes[0]["interactive"]["body"]["text"]
    assert "2 x Bolsa 5 kg" in texto
    assert "1 x Bolsa 3 kg" in texto
    assert "3 x Bolsa 10 kg" in texto
    assert "Total parcial: $93.00" in texto
