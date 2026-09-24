"""Primer contacto: saluda y abre el menú en un solo mensaje saliente."""

from src.fsm.dispatcher import MensajeEntrante, ResultadoHandler
from src.fsm.handlers.menu_principal import crear_menu
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente


def atender_idle(
    _mensaje: MensajeEntrante,
    contexto: dict,
    cliente: Cliente,
    primera_interaccion: bool,
) -> ResultadoHandler:
    """Saluda incluso si el primer mensaje es audio o imagen.

    El nombre de perfil puede venir en el primer webhook; por eso el saludo
    personalizado exige una conversación previa además de un nombre.
    """
    if not primera_interaccion and cliente.nombre:
        saludo = f"¡Hola de nuevo, {cliente.nombre}! ¿En qué te ayudo hoy?"
    else:
        saludo = (
            "¡Hola! Soy el asistente de pedidos de Hielon de León. "
            "Te ayudo a levantar tu pedido de hielo en unos pasos."
        )

    return ResultadoHandler(
        siguiente_estado=EstadoConversacion.MENU_PRINCIPAL,
        contexto=contexto,
        mensajes_salientes=[crear_menu(saludo)],
    )
