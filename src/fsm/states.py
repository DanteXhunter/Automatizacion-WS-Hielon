"""Estados y transiciones permitidas de la conversación de WhatsApp."""

from enum import Enum


class EstadoConversacion(str, Enum):
    """Situaciones persistibles de una conversación con un cliente."""

    IDLE = "IDLE"
    MENU_PRINCIPAL = "MENU_PRINCIPAL"
    SELECCIONANDO_PRODUCTO = "SELECCIONANDO_PRODUCTO"
    CAPTURANDO_CANTIDAD = "CAPTURANDO_CANTIDAD"
    AGREGAR_MAS_O_CONTINUAR = "AGREGAR_MAS_O_CONTINUAR"
    CAPTURANDO_DIRECCION = "CAPTURANDO_DIRECCION"
    REVISANDO_RESUMEN = "REVISANDO_RESUMEN"
    SELECCIONANDO_MODIFICACION = "SELECCIONANDO_MODIFICACION"
    CONFIRMANDO_CANCELACION = "CONFIRMANDO_CANCELACION"
    EN_ASESOR_HUMANO = "EN_ASESOR_HUMANO"
    FUERA_DE_HORARIO = "FUERA_DE_HORARIO"


# Los bucles al mismo estado son válidos: representan un dato inválido que se
# vuelve a pedir sin perder el punto actual de la conversación.
TRANSICIONES_VALIDAS: dict[EstadoConversacion, frozenset[EstadoConversacion]] = {
    EstadoConversacion.IDLE: frozenset(
        {EstadoConversacion.IDLE, EstadoConversacion.MENU_PRINCIPAL}
    ),
    EstadoConversacion.MENU_PRINCIPAL: frozenset(
        {
            EstadoConversacion.MENU_PRINCIPAL,
            EstadoConversacion.SELECCIONANDO_PRODUCTO,
            EstadoConversacion.EN_ASESOR_HUMANO,
        }
    ),
    EstadoConversacion.SELECCIONANDO_PRODUCTO: frozenset(
        {
            EstadoConversacion.SELECCIONANDO_PRODUCTO,
            EstadoConversacion.MENU_PRINCIPAL,
            EstadoConversacion.CAPTURANDO_CANTIDAD,
            EstadoConversacion.CONFIRMANDO_CANCELACION,
            EstadoConversacion.EN_ASESOR_HUMANO,
        }
    ),
    EstadoConversacion.CAPTURANDO_CANTIDAD: frozenset(
        {
            EstadoConversacion.CAPTURANDO_CANTIDAD,
            EstadoConversacion.SELECCIONANDO_PRODUCTO,
            EstadoConversacion.AGREGAR_MAS_O_CONTINUAR,
            EstadoConversacion.CONFIRMANDO_CANCELACION,
            EstadoConversacion.EN_ASESOR_HUMANO,
        }
    ),
    EstadoConversacion.AGREGAR_MAS_O_CONTINUAR: frozenset(
        {
            EstadoConversacion.AGREGAR_MAS_O_CONTINUAR,
            EstadoConversacion.CAPTURANDO_CANTIDAD,
            EstadoConversacion.SELECCIONANDO_PRODUCTO,
            EstadoConversacion.CAPTURANDO_DIRECCION,
            EstadoConversacion.CONFIRMANDO_CANCELACION,
            EstadoConversacion.EN_ASESOR_HUMANO,
        }
    ),
    EstadoConversacion.CAPTURANDO_DIRECCION: frozenset(
        {
            EstadoConversacion.CAPTURANDO_DIRECCION,
            EstadoConversacion.AGREGAR_MAS_O_CONTINUAR,
            EstadoConversacion.REVISANDO_RESUMEN,
            EstadoConversacion.CONFIRMANDO_CANCELACION,
        }
    ),
    EstadoConversacion.REVISANDO_RESUMEN: frozenset(
        {
            EstadoConversacion.REVISANDO_RESUMEN,
            EstadoConversacion.IDLE,
            EstadoConversacion.SELECCIONANDO_MODIFICACION,
            EstadoConversacion.CONFIRMANDO_CANCELACION,
            EstadoConversacion.EN_ASESOR_HUMANO,
        }
    ),
    EstadoConversacion.SELECCIONANDO_MODIFICACION: frozenset(
        {
            EstadoConversacion.SELECCIONANDO_MODIFICACION,
            EstadoConversacion.SELECCIONANDO_PRODUCTO,
            EstadoConversacion.CAPTURANDO_DIRECCION,
            EstadoConversacion.REVISANDO_RESUMEN,
            EstadoConversacion.CONFIRMANDO_CANCELACION,
            EstadoConversacion.EN_ASESOR_HUMANO,
        }
    ),
    EstadoConversacion.CONFIRMANDO_CANCELACION: frozenset(
        {
            EstadoConversacion.CONFIRMANDO_CANCELACION,
            EstadoConversacion.IDLE,
            EstadoConversacion.REVISANDO_RESUMEN,
        }
    ),
    EstadoConversacion.EN_ASESOR_HUMANO: frozenset(
        {
            EstadoConversacion.EN_ASESOR_HUMANO,
            EstadoConversacion.IDLE,
        }
    ),
    # En v1 es una condición previa a la FSM; queda solo como referencia.
    EstadoConversacion.FUERA_DE_HORARIO: frozenset(
        {EstadoConversacion.FUERA_DE_HORARIO}
    ),
}


TRANSICIONES_ATRAS: dict[EstadoConversacion, EstadoConversacion] = {
    EstadoConversacion.SELECCIONANDO_PRODUCTO: EstadoConversacion.MENU_PRINCIPAL,
    EstadoConversacion.CAPTURANDO_CANTIDAD: EstadoConversacion.SELECCIONANDO_PRODUCTO,
    EstadoConversacion.AGREGAR_MAS_O_CONTINUAR: EstadoConversacion.CAPTURANDO_CANTIDAD,
    EstadoConversacion.CAPTURANDO_DIRECCION: EstadoConversacion.AGREGAR_MAS_O_CONTINUAR,
    EstadoConversacion.SELECCIONANDO_MODIFICACION: EstadoConversacion.REVISANDO_RESUMEN,
}


def es_transicion_valida(
    origen: EstadoConversacion,
    destino: EstadoConversacion,
) -> bool:
    """Indica si el estado destino está permitido desde el estado origen."""
    return destino in TRANSICIONES_VALIDAS[origen]
