"""Enrutamiento del menú por ID y límite de intentos inválidos."""

import asyncio
from decimal import Decimal
from uuid import uuid4

from src.fsm.dispatcher import MensajeEntrante
from src.fsm.handlers.menu_principal import atender_menu_principal, crear_menu
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente
from src.models.producto import Producto

CLIENTE = Cliente(telefono="+5214771234567")


class SesionProductos:
    def __init__(self, productos=()):
        self.productos = list(productos)

    async def exec(self, _consulta):
        class Resultado:
            def __init__(self, productos):
                self.productos = productos

            def all(self):
                return self.productos

            def first(self):
                return self.productos[0] if self.productos else None

        return Resultado(self.productos)


def _producto(nombre: str) -> Producto:
    return Producto(
        id=uuid4(), nombre=nombre, peso_kg=Decimal(5), precio=Decimal("1.00")
    )


def _menu(mensaje, contexto, session=None):
    return asyncio.run(
        atender_menu_principal(
            mensaje, contexto, CLIENTE, False, session=session or SesionProductos()
        )
    )


def _boton(identificador: str) -> MensajeEntrante:
    return MensajeEntrante(tipo="boton", valor=identificador, payload={})


def test_menu_tiene_tres_botones_con_ids_unicos() -> None:
    botones = crear_menu()["interactive"]["action"]["buttons"]
    assert [boton["reply"]["id"] for boton in botones] == [
        "hacer_pedido",
        "consultar",
        "asesor",
    ]
    assert all(len(boton["reply"]["title"]) <= 20 for boton in botones)


def test_hacer_pedido_enruta_por_id_y_reinicia_intentos() -> None:
    producto = _producto("Bolsa 5 kg")
    resultado = _menu(
        _boton("hacer_pedido"), {"intentos_invalidos": 2}, SesionProductos([producto])
    )
    assert resultado.siguiente_estado == EstadoConversacion.SELECCIONANDO_PRODUCTO
    assert "intentos_invalidos" not in resultado.contexto
    filas = resultado.mensajes_salientes[0]["interactive"]["action"]["sections"][0][
        "rows"
    ]
    assert filas[0] == {"id": str(producto.id), "title": "Bolsa 5 kg"}
    assert filas[-1] == {"id": "volver", "title": "Volver"}


def test_titulo_visible_no_sustituye_id_del_boton() -> None:
    resultado = _menu(
        MensajeEntrante(tipo="texto", valor="Hacer pedido", payload={}), {}
    )
    assert resultado.siguiente_estado == EstadoConversacion.MENU_PRINCIPAL
    assert resultado.contexto["intentos_invalidos"] == 1


def test_consultar_sin_pedidos_vuelve_al_menu() -> None:
    resultado = _menu(_boton("consultar"), {})
    assert resultado.siguiente_estado == EstadoConversacion.MENU_PRINCIPAL
    assert (
        "No tienes pedidos activos"
        in resultado.mensajes_salientes[0]["interactive"]["body"]["text"]
    )


def test_consultar_con_pedido_muestra_estado_sin_guardar_dato_temporal() -> None:
    resultado = _menu(
        _boton("consultar"),
        {"_pedido_activo": {"numero_orden": "2026-0142", "estado": "pendiente"}},
    )
    texto = resultado.mensajes_salientes[0]["interactive"]["body"]["text"]
    assert "2026-0142" in texto
    assert "pendiente" in texto
    assert "_pedido_activo" not in resultado.contexto


def test_asesor_y_tres_entradas_invalidas_silencian_el_bot() -> None:
    asesor = _menu(_boton("asesor"), {})
    invalido = _menu(
        MensajeEntrante(tipo="texto", valor="???", payload={}),
        {"intentos_invalidos": 2},
    )
    assert asesor.siguiente_estado == EstadoConversacion.EN_ASESOR_HUMANO
    assert invalido.siguiente_estado == EstadoConversacion.EN_ASESOR_HUMANO
    assert invalido.contexto["intentos_invalidos"] == 3
    assert asesor.mensajes_salientes == invalido.mensajes_salientes == []
