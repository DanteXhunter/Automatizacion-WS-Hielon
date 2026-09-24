"""Resumen, edición de productos y cancelación de pedidos borrador."""

from typing import Any
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import settings
from src.fsm.dispatcher import MensajeEntrante, ResultadoHandler
from src.fsm.handlers.menu_principal import crear_selector_productos
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente
from src.models.direccion import Direccion
from src.models.pedido import EstadoPedido
from src.services.pedido_service import (
    PedidoNoEncontradoError,
    PedidoSinDireccionError,
    PedidoSinItemsError,
    TransicionPedidoInvalidaError,
    calcular_total_borrador,
    cambiar_estado,
    confirmar_pedido,
    listar_items_borrador,
    listar_productos_activos,
    obtener_borrador,
    vaciar_items_borrador,
)
from src.utils.datetime import ahora_local, es_horario_laboral, paso_hora_corte

ACCIONES_RESUMEN = (
    ("confirmar", "Confirmar pedido"),
    ("modificar", "Modificar pedido"),
    ("cancelar", "Cancelar pedido"),
    ("asesor", "Hablar con asesor"),
)


def debe_sugerir_entrega_manana() -> bool:
    """Limita la advertencia al periodo hábil posterior al corte."""
    momento = ahora_local()
    return es_horario_laboral(momento) and paso_hora_corte(momento)


def _botones(opciones: tuple[tuple[str, str], ...]) -> list[dict[str, Any]]:
    return [
        {"type": "reply", "reply": {"id": identificador, "title": titulo}}
        for identificador, titulo in opciones
    ]


def crear_mensaje_modificacion(texto: str = "¿Qué deseas modificar?") -> dict[str, Any]:
    """Crea el menú de edición del borrador con sus tres acciones."""
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": texto},
            "action": {
                "buttons": _botones(
                    (
                        ("productos", "Productos"),
                        ("direccion", "Dirección"),
                        ("volver", "Volver"),
                    )
                )
            },
        },
    }


def crear_mensaje_cancelacion() -> dict[str, Any]:
    """Pide confirmación explícita antes de marcar el borrador cancelado."""
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "¿Seguro que deseas cancelar tu pedido?"},
            "action": {
                "buttons": _botones(
                    (("si_cancelar", "Sí, cancelar"), ("no_regresar", "No, regresar"))
                )
            },
        },
    }


async def crear_mensaje_resumen(
    session: AsyncSession,
    cliente: Cliente,
    pedido_borrador_id: UUID | None,
) -> dict[str, Any]:
    """Construye el resumen con datos persistidos y recalcula su total."""
    pedido = await obtener_borrador(session, cliente.id, pedido_borrador_id)
    if pedido is None:
        return {"type": "text", "body": "No encontré un pedido borrador para revisar."}

    items = await listar_items_borrador(session, pedido.id)
    if not items:
        return {
            "type": "text",
            "body": "Tu pedido no tiene productos. Agrega al menos uno para continuar.",
        }

    direccion = None
    if pedido.direccion_id is not None:
        direccion = (
            await session.exec(
                select(Direccion).where(
                    Direccion.id == pedido.direccion_id,
                    Direccion.cliente_id == cliente.id,
                )
            )
        ).first()
    if direccion is None:
        return {
            "type": "text",
            "body": "Falta la dirección de entrega. Registra una para revisar el pedido.",
        }

    pedido.total = await calcular_total_borrador(session, pedido.id)
    detalle_direccion = direccion.texto or (
        f"Ubicación ({direccion.latitud}, {direccion.longitud})"
    )
    lineas: list[str] = []
    if debe_sugerir_entrega_manana():
        corte = settings.hora_corte_mismo_dia.strftime("%H:%M")
        lineas.extend(
            [
                (
                    f"Ya pasó nuestro horario de corte de las {corte}. "
                    "Este pedido probablemente saldría mañana temprano. "
                    "Si lo necesitas hoy, con gusto te comunicamos con un asesor."
                ),
                "",
            ]
        )
    lineas.extend(["Resumen de tu pedido:", ""])
    lineas.extend(
        f"- {item.cantidad} x {producto.nombre} .......... ${item.subtotal:.2f}"
        for item, producto in items
    )
    lineas.extend(
        [
            "",
            f"Entrega en: {detalle_direccion}",
            f"Total: ${pedido.total:.2f}",
            "",
            "Los precios no incluyen IVA ni envío.",
        ]
    )
    if any(item.precio_unitario == 0 for item, _ in items):
        lineas.append("Nota: los precios del catálogo están pendientes de confirmar.")

    return {
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "\n".join(lineas)},
            "action": {
                "button": "Ver opciones",
                "sections": [
                    {
                        "title": "¿Qué deseas hacer?",
                        "rows": [
                            {"id": identificador, "title": titulo}
                            for identificador, titulo in ACCIONES_RESUMEN
                        ],
                    }
                ],
            },
        },
    }


async def atender_revision_resumen(
    mensaje: MensajeEntrante,
    contexto: dict[str, Any],
    cliente: Cliente,
    _primera_interaccion: bool,
    *,
    session: AsyncSession,
    pedido_borrador_id: UUID | None,
) -> ResultadoHandler:
    """Muestra el resumen y enruta las cuatro decisiones finales."""
    if mensaje.tipo == "boton" and mensaje.valor == "modificar":
        return ResultadoHandler(
            EstadoConversacion.SELECCIONANDO_MODIFICACION,
            contexto,
            [crear_mensaje_modificacion()],
        )
    if mensaje.tipo == "boton" and mensaje.valor == "cancelar":
        return ResultadoHandler(
            EstadoConversacion.CONFIRMANDO_CANCELACION,
            contexto,
            [crear_mensaje_cancelacion()],
        )
    if mensaje.tipo == "boton" and mensaje.valor == "asesor":
        contexto["handoff_motivo"] = "Solicitud del cliente"
        return ResultadoHandler(
            EstadoConversacion.EN_ASESOR_HUMANO,
            contexto,
            [
                {
                    "type": "text",
                    "body": "Te comunico con un asesor, en un momento te atienden.",
                }
            ],
        )
    if mensaje.tipo == "boton" and mensaje.valor == "confirmar":
        try:
            confirmacion = await confirmar_pedido(
                session,
                cliente.id,
                pedido_borrador_id,
            )
        except PedidoSinItemsError:
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
                            "body": "Tu pedido no tiene productos y no hay catálogo disponible. Te comunico con un asesor.",
                        }
                    ]
                ),
            )
        except PedidoSinDireccionError:
            from src.fsm.handlers.direccion import mensaje_inicial_direccion

            return ResultadoHandler(
                EstadoConversacion.CAPTURANDO_DIRECCION,
                contexto,
                [await mensaje_inicial_direccion(session, cliente.id)],
            )
        except (PedidoNoEncontradoError, TransicionPedidoInvalidaError):
            contexto.clear()
            contexto["_limpiar_pedido_borrador"] = True
            return ResultadoHandler(
                EstadoConversacion.IDLE,
                contexto,
                [
                    {
                        "type": "text",
                        "body": "No pude confirmar ese borrador. Escribe nuevamente para iniciar un pedido.",
                    }
                ],
            )

        pedido = confirmacion.pedido
        contexto.clear()
        contexto["_limpiar_pedido_borrador"] = True
        texto = (
            f"¡Listo! Tu pedido #{pedido.numero_orden} quedó registrado.\n"
            f"Total: ${pedido.total:.2f}. Te avisamos cuando vaya en camino."
        )
        if confirmacion.es_primer_pedido:
            texto += (
                "\nNuestro equipo confirmará el horario de entrega. "
                "El pago se realiza contra entrega."
            )
        return ResultadoHandler(
            EstadoConversacion.IDLE,
            contexto,
            [{"type": "text", "body": texto}],
        )

    resumen = await crear_mensaje_resumen(session, cliente, pedido_borrador_id)
    return ResultadoHandler(
        EstadoConversacion.REVISANDO_RESUMEN,
        contexto,
        [resumen],
    )


async def atender_seleccion_modificacion(
    mensaje: MensajeEntrante,
    contexto: dict[str, Any],
    cliente: Cliente,
    _primera_interaccion: bool,
    *,
    session: AsyncSession,
    pedido_borrador_id: UUID | None,
) -> ResultadoHandler:
    """Modifica productos con confirmación previa o conserva el carrito."""
    if contexto.get("confirmar_recaptura_productos"):
        if mensaje.tipo == "boton" and mensaje.valor == "no_rehacer":
            contexto.pop("confirmar_recaptura_productos", None)
            return ResultadoHandler(
                EstadoConversacion.REVISANDO_RESUMEN,
                contexto,
                [await crear_mensaje_resumen(session, cliente, pedido_borrador_id)],
            )
        if mensaje.tipo == "boton" and mensaje.valor == "si_rehacer":
            contexto.pop("confirmar_recaptura_productos", None)
            pedido = await obtener_borrador(session, cliente.id, pedido_borrador_id)
            if pedido is None:
                return ResultadoHandler(
                    EstadoConversacion.REVISANDO_RESUMEN,
                    contexto,
                    [
                        {
                            "type": "text",
                            "body": "No encontré el borrador. No se modificó ningún producto.",
                        }
                    ],
                )
            productos = await listar_productos_activos(session)
            if not productos:
                contexto["handoff_motivo"] = "Catálogo no disponible"
                return ResultadoHandler(
                    EstadoConversacion.EN_ASESOR_HUMANO,
                    contexto,
                    [
                        {
                            "type": "text",
                            "body": "No hay productos disponibles. Conservé tu carrito actual para que no pierdas el pedido.",
                        }
                    ],
                )
            await vaciar_items_borrador(session, pedido)
            contexto.pop("producto_actual", None)
            contexto.pop("ultimo_item_id", None)
            return ResultadoHandler(
                EstadoConversacion.SELECCIONANDO_PRODUCTO,
                contexto,
                [crear_selector_productos(productos)],
            )
        return ResultadoHandler(
            EstadoConversacion.SELECCIONANDO_MODIFICACION,
            contexto,
            [_boton_confirmar_recaptura()],
        )

    if mensaje.tipo == "boton" and mensaje.valor == "productos":
        contexto["confirmar_recaptura_productos"] = True
        return ResultadoHandler(
            EstadoConversacion.SELECCIONANDO_MODIFICACION,
            contexto,
            [_boton_confirmar_recaptura()],
        )
    if mensaje.tipo == "boton" and mensaje.valor == "direccion":
        from src.fsm.handlers.direccion import mensaje_inicial_direccion

        return ResultadoHandler(
            EstadoConversacion.CAPTURANDO_DIRECCION,
            contexto,
            [await mensaje_inicial_direccion(session, cliente.id)],
        )
    return ResultadoHandler(
        EstadoConversacion.SELECCIONANDO_MODIFICACION,
        contexto,
        [crear_mensaje_modificacion("Elige Productos, Dirección o Volver.")],
    )


def _boton_confirmar_recaptura() -> dict[str, Any]:
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Vamos a capturar los productos de nuevo. "
                "Se quitarán los productos actuales y se conservará la dirección. ¿Continuamos?"
            },
            "action": {
                "buttons": _botones(
                    (("si_rehacer", "Sí, recapturar"), ("no_rehacer", "No, volver"))
                )
            },
        },
    }


async def atender_confirmacion_cancelacion(
    mensaje: MensajeEntrante,
    contexto: dict[str, Any],
    cliente: Cliente,
    _primera_interaccion: bool,
    *,
    session: AsyncSession,
    pedido_borrador_id: UUID | None,
) -> ResultadoHandler:
    """Cancela solo por confirmación explícita y conserva el historial del pedido."""
    if mensaje.tipo == "boton" and mensaje.valor == "si_cancelar":
        pedido = await obtener_borrador(session, cliente.id, pedido_borrador_id)
        if pedido is None:
            contexto.clear()
            contexto["_limpiar_pedido_borrador"] = True
            return ResultadoHandler(
                EstadoConversacion.IDLE,
                contexto,
                [
                    {
                        "type": "text",
                        "body": "No encontré un pedido pendiente de cancelar.",
                    }
                ],
            )

        cambiar_estado(pedido, EstadoPedido.CANCELADO_CLIENTE)
        contexto.clear()
        contexto["_limpiar_pedido_borrador"] = True
        return ResultadoHandler(
            EstadoConversacion.IDLE,
            contexto,
            [
                {
                    "type": "text",
                    "body": "Listo, cancelamos tu pedido. Aquí estamos cuando nos necesites.",
                }
            ],
        )
    if mensaje.tipo == "boton" and mensaje.valor == "no_regresar":
        return ResultadoHandler(
            EstadoConversacion.REVISANDO_RESUMEN,
            contexto,
            [await crear_mensaje_resumen(session, cliente, pedido_borrador_id)],
        )
    return ResultadoHandler(
        EstadoConversacion.CONFIRMANDO_CANCELACION,
        contexto,
        [crear_mensaje_cancelacion()],
    )
