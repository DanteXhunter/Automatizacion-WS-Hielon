"""El primer contacto usa un saludo y un menú en un solo envío."""

from src.fsm.dispatcher import MensajeEntrante
from src.fsm.handlers.idle import atender_idle
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente


def test_cliente_nuevo_recibe_bienvenida_aunque_meta_mande_nombre() -> None:
    cliente = Cliente(telefono="+5214771234567", nombre="Ana")
    mensaje = MensajeEntrante(tipo="image", valor=None, payload={})

    resultado = atender_idle(mensaje, {}, cliente, True)

    assert resultado.siguiente_estado == EstadoConversacion.MENU_PRINCIPAL
    assert len(resultado.mensajes_salientes) == 1
    assert (
        "Soy el asistente"
        in resultado.mensajes_salientes[0]["interactive"]["body"]["text"]
    )
    assert cliente.opt_in_recordatorios is False


def test_cliente_con_conversacion_previa_recibe_saludo_personalizado() -> None:
    cliente = Cliente(telefono="+5214771234567", nombre="Ana")
    mensaje = MensajeEntrante(tipo="texto", valor="quiero 10 bolsas", payload={})

    resultado = atender_idle(mensaje, {}, cliente, False)

    assert resultado.siguiente_estado == EstadoConversacion.MENU_PRINCIPAL
    assert (
        "Hola de nuevo, Ana"
        in resultado.mensajes_salientes[0]["interactive"]["body"]["text"]
    )
