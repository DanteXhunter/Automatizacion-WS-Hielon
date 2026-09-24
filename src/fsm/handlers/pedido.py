"""Selección de productos, captura de cantidades y operaciones del carrito."""

import re
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from src.fsm.dispatcher import MensajeEntrante, ResultadoHandler
from src.fsm.handlers.menu_principal import crear_menu, crear_selector_productos
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente
from src.models.producto import Producto
from src.services.pedido_service import (
    agregar_item_borrador,
    calcular_total_borrador,
    eliminar_item_borrador,
    listar_items_borrador,
    listar_productos_activos,
    obtener_o_crear_borrador,
    obtener_producto_activo,
)

CANTIDAD_MAXIMA = 500
BOTON_VOLVER = ("volver", "Volver")


def _preguntar_cantidad(producto: Producto, texto: str | None = None) -> dict[str, Any]:
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": texto or f"¿Cuántas bolsas de {producto.nombre} necesitas?"
            },
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "volver", "title": "Volver"}}
                ]
            },
        },
    }


def _preguntar_accion_carrito(
    items: list[tuple[Any, Producto]], total: Decimal
) -> dict[str, Any]:
    lineas = ["Tu pedido va así:"]
    lineas.extend(
        f"- {item.cantidad} x {producto.nombre} .... ${item.subtotal:.2f}"
        for item, producto in items
    )
    lineas.append(f"Total parcial: ${total:.2f}")
    if any(item.precio_unitario == 0 for item, _ in items):
        lineas.append("Nota: los precios del catálogo están pendientes de confirmar.")
    lineas.append("¿Quieres agregar otro producto o continuar?")
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "\n".join(lineas)},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": "agregar_otro", "title": "Agregar otro"},
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "continuar", "title": "Continuar"},
                    },
                    {"type": "reply", "reply": {"id": "volver", "title": "Volver"}},
                ]
            },
        },
    }


async def atender_seleccion_producto(
    mensaje: MensajeEntrante,
    contexto: dict[str, Any],
    _cliente: Cliente,
    _primera_interaccion: bool,
    *,
    session: AsyncSession,
) -> ResultadoHandler:
    """Valida UUID y disponibilidad antes de almacenar el producto elegido."""
    if mensaje.tipo == "boton" and mensaje.valor == "volver":
        contexto.pop("producto_actual", None)
        return ResultadoHandler(
            EstadoConversacion.MENU_PRINCIPAL,
            contexto,
            [crear_menu()],
        )

    producto_id: UUID | None = None
    if mensaje.tipo == "boton" and mensaje.valor:
        try:
            producto_id = UUID(mensaje.valor)
        except ValueError:
            pass
    producto = (
        await obtener_producto_activo(session, producto_id)
        if producto_id is not None
        else None
    )
    if producto is not None:
        contexto.pop("intentos_invalidos", None)
        contexto["producto_actual"] = str(producto.id)
        return ResultadoHandler(
            EstadoConversacion.CAPTURANDO_CANTIDAD,
            contexto,
            [_preguntar_cantidad(producto)],
        )

    productos = await listar_productos_activos(session)
    if not productos:
        contexto.pop("producto_actual", None)
        return ResultadoHandler(
            EstadoConversacion.EN_ASESOR_HUMANO,
            contexto,
            [
                {
                    "type": "text",
                    "body": "No hay productos disponibles. Te comunico con un asesor.",
                }
            ],
        )

    intentos = int(contexto.get("intentos_invalidos", 0)) + 1
    contexto["intentos_invalidos"] = intentos
    if intentos >= 3:
        return ResultadoHandler(EstadoConversacion.EN_ASESOR_HUMANO, contexto, [])
    return ResultadoHandler(
        EstadoConversacion.SELECCIONANDO_PRODUCTO,
        contexto,
        [crear_selector_productos(productos)],
    )


async def atender_captura_cantidad(
    mensaje: MensajeEntrante,
    contexto: dict[str, Any],
    cliente: Cliente,
    _primera_interaccion: bool,
    *,
    session: AsyncSession,
    pedido_borrador_id: UUID | None,
) -> ResultadoHandler:
    """Acepta solo enteros positivos acotados y persiste el renglón del pedido."""
    if mensaje.tipo == "boton" and mensaje.valor == "volver":
        contexto.pop("producto_actual", None)
        productos = await listar_productos_activos(session)
        if not productos:
            return ResultadoHandler(
                EstadoConversacion.EN_ASESOR_HUMANO,
                contexto,
                [
                    {
                        "type": "text",
                        "body": "No hay productos disponibles. Te comunico con un asesor.",
                    }
                ],
            )
        return ResultadoHandler(
            EstadoConversacion.SELECCIONANDO_PRODUCTO,
            contexto,
            [crear_selector_productos(productos)],
        )

    producto_id = _uuid_desde_contexto(contexto.get("producto_actual"))
    producto = (
        await obtener_producto_activo(session, producto_id)
        if producto_id is not None
        else None
    )
    if producto is None:
        contexto.pop("producto_actual", None)
        productos = await listar_productos_activos(session)
        return ResultadoHandler(
            EstadoConversacion.SELECCIONANDO_PRODUCTO,
            contexto,
            (
                [crear_selector_productos(productos)]
                if productos
                else [
                    {
                        "type": "text",
                        "body": "No hay productos disponibles. Te comunico con un asesor.",
                    }
                ]
            ),
        )

    texto = mensaje.valor or ""
    cantidad = (
        int(texto)
        if mensaje.tipo == "texto"
        and len(texto) <= 3
        and re.fullmatch(r"[0-9]+", texto)
        else 0
    )
    if not 1 <= cantidad <= CANTIDAD_MAXIMA:
        return ResultadoHandler(
            EstadoConversacion.CAPTURANDO_CANTIDAD,
            contexto,
            [
                _preguntar_cantidad(
                    producto,
                    f"Necesito el número de bolsas (1–{CANTIDAD_MAXIMA}) para "
                    f"{producto.nombre}. Por ejemplo: 10",
                )
            ],
        )

    pedido = await obtener_o_crear_borrador(session, cliente.id, pedido_borrador_id)
    item = await agregar_item_borrador(session, pedido, producto, cantidad)
    contexto["pedido_borrador_id"] = str(pedido.id)
    contexto["ultimo_item_id"] = str(item.id)
    contexto.pop("producto_actual", None)
    contexto.pop("intentos_invalidos", None)
    items = await listar_items_borrador(session, pedido.id)
    total = await calcular_total_borrador(session, pedido.id)
    return ResultadoHandler(
        EstadoConversacion.AGREGAR_MAS_O_CONTINUAR,
        contexto,
        [_preguntar_accion_carrito(items, total)],
    )


async def atender_carrito(
    mensaje: MensajeEntrante,
    contexto: dict[str, Any],
    cliente: Cliente,
    _primera_interaccion: bool,
    *,
    session: AsyncSession,
    pedido_borrador_id: UUID | None,
) -> ResultadoHandler:
    """Presenta el carrito desde DB y permite agregar, continuar o editar."""
    pedido = await obtener_o_crear_borrador(session, cliente.id, pedido_borrador_id)
    items = await listar_items_borrador(session, pedido.id)

    if mensaje.tipo == "boton" and mensaje.valor == "continuar":
        return ResultadoHandler(
            EstadoConversacion.CAPTURANDO_DIRECCION,
            contexto,
            [{"type": "text", "body": "¿A qué dirección llevamos tu pedido?"}],
        )

    if mensaje.tipo == "boton" and mensaje.valor == "agregar_otro":
        productos = await listar_productos_activos(session)
        if not productos:
            return ResultadoHandler(
                EstadoConversacion.EN_ASESOR_HUMANO,
                contexto,
                [
                    {
                        "type": "text",
                        "body": "No hay productos disponibles. Te comunico con un asesor.",
                    }
                ],
            )
        return ResultadoHandler(
            EstadoConversacion.SELECCIONANDO_PRODUCTO,
            contexto,
            [crear_selector_productos(productos)],
        )

    if mensaje.tipo == "boton" and mensaje.valor == "volver":
        ultimo_item_id = _uuid_desde_contexto(contexto.get("ultimo_item_id"))
        ultimo = next(
            ((item, producto) for item, producto in items if item.id == ultimo_item_id),
            None,
        )
        if ultimo is not None:
            item, producto = ultimo
            await eliminar_item_borrador(session, pedido, item.id)
            contexto["producto_actual"] = str(producto.id)
            contexto.pop("ultimo_item_id", None)
            return ResultadoHandler(
                EstadoConversacion.CAPTURANDO_CANTIDAD,
                contexto,
                [_preguntar_cantidad(producto)],
            )

    total = await calcular_total_borrador(session, pedido.id)
    return ResultadoHandler(
        EstadoConversacion.AGREGAR_MAS_O_CONTINUAR,
        contexto,
        (
            [_preguntar_accion_carrito(items, total)]
            if items
            else [
                {
                    "type": "text",
                    "body": "Tu carrito está vacío. Elige un producto para continuar.",
                }
            ]
        ),
    )


def _uuid_desde_contexto(valor: Any) -> UUID | None:
    if not isinstance(valor, str):
        return None
    try:
        return UUID(valor)
    except ValueError:
        return None
