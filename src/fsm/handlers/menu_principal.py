"""Opciones del menú principal y respuesta a sus botones de WhatsApp."""

from typing import Any

from src.fsm.dispatcher import MensajeEntrante, ResultadoHandler
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente

BOTONES_MENU = (
    ("hacer_pedido", "Hacer pedido"),
    ("consultar", "Consultar pedido"),
    ("asesor", "Hablar con asesor"),
)


def _botones(opciones: tuple[tuple[str, str], ...]) -> list[dict[str, Any]]:
    return [
        {"type": "reply", "reply": {"id": identificador, "title": titulo}}
        for identificador, titulo in opciones
    ]


def crear_menu(texto: str = "¿En qué te ayudo?") -> dict[str, Any]:
    """Construye un único mensaje interactivo con los tres botones del menú."""
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": texto},
            "action": {"buttons": _botones(BOTONES_MENU)},
        },
    }


def atender_menu_principal(
    mensaje: MensajeEntrante,
    contexto: dict[str, Any],
    _cliente: Cliente,
    _primera_interaccion: bool,
) -> ResultadoHandler:
    """Enruta usando el ID estable del botón, nunca su título visible."""
    if mensaje.tipo == "boton" and mensaje.valor in {id for id, _ in BOTONES_MENU}:
        contexto.pop("intentos_invalidos", None)

        if mensaje.valor == "hacer_pedido":
            return ResultadoHandler(
                siguiente_estado=EstadoConversacion.SELECCIONANDO_PRODUCTO,
                contexto=contexto,
                mensajes_salientes=[
                    {
                        "type": "interactive",
                        "interactive": {
                            "type": "button",
                            "body": {"text": "¿Qué presentación de hielo necesitas?"},
                            "action": {
                                "buttons": _botones(
                                    (
                                        ("bolsa_3kg", "Bolsa 3 kg"),
                                        ("bolsa_5kg", "Bolsa 5 kg"),
                                        ("bolsa_10kg", "Bolsa 10 kg"),
                                    )
                                )
                            },
                        },
                    }
                ],
            )

        if mensaje.valor == "consultar":
            pedido = contexto.pop("_pedido_activo", None)
            if pedido is None:
                texto = "No tienes pedidos activos. ¿En qué te ayudo?"
            else:
                numero = pedido["numero_orden"] or "sin número"
                texto = (
                    f"Tu pedido {numero} está {pedido['estado']}. " "¿En qué te ayudo?"
                )
            return ResultadoHandler(
                siguiente_estado=EstadoConversacion.MENU_PRINCIPAL,
                contexto=contexto,
                mensajes_salientes=[crear_menu(texto)],
            )

        return ResultadoHandler(
            siguiente_estado=EstadoConversacion.EN_ASESOR_HUMANO,
            contexto=contexto,
            mensajes_salientes=[],
        )

    intentos = int(contexto.get("intentos_invalidos", 0)) + 1
    contexto["intentos_invalidos"] = intentos
    if intentos >= 3:
        return ResultadoHandler(
            siguiente_estado=EstadoConversacion.EN_ASESOR_HUMANO,
            contexto=contexto,
            mensajes_salientes=[],
        )

    return ResultadoHandler(
        siguiente_estado=EstadoConversacion.MENU_PRINCIPAL,
        contexto=contexto,
        mensajes_salientes=[crear_menu("Por favor elige una de las opciones.")],
    )


def atender_asesor(
    _mensaje: MensajeEntrante,
    contexto: dict[str, Any],
    _cliente: Cliente,
    _primera_interaccion: bool,
) -> ResultadoHandler:
    """Mantiene silenciado al bot cuando la conversación espera a un humano."""
    return ResultadoHandler(
        siguiente_estado=EstadoConversacion.EN_ASESOR_HUMANO,
        contexto=contexto,
        mensajes_salientes=[],
    )
