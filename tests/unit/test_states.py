from src.fsm.states import (
    TRANSICIONES_ATRAS,
    TRANSICIONES_VALIDAS,
    EstadoConversacion,
    es_transicion_valida,
)


def test_enum_declara_los_once_estados_documentados():
    assert len(EstadoConversacion) == 11
    assert EstadoConversacion.FUERA_DE_HORARIO.value == "FUERA_DE_HORARIO"


def test_cada_estado_tiene_un_mapa_de_transiciones():
    assert set(TRANSICIONES_VALIDAS) == set(EstadoConversacion)


def test_transiciones_principales_del_pedido_son_validas():
    assert es_transicion_valida(
        EstadoConversacion.IDLE,
        EstadoConversacion.MENU_PRINCIPAL,
    )
    assert es_transicion_valida(
        EstadoConversacion.CAPTURANDO_DIRECCION,
        EstadoConversacion.REVISANDO_RESUMEN,
    )
    assert es_transicion_valida(
        EstadoConversacion.REVISANDO_RESUMEN,
        EstadoConversacion.EN_ASESOR_HUMANO,
    )


def test_transicion_que_salta_pasos_es_invalida():
    assert not es_transicion_valida(
        EstadoConversacion.MENU_PRINCIPAL,
        EstadoConversacion.REVISANDO_RESUMEN,
    )


def test_mapa_atras_centraliza_los_cinco_estados_con_boton_volver():
    assert TRANSICIONES_ATRAS == {
        EstadoConversacion.SELECCIONANDO_PRODUCTO: EstadoConversacion.MENU_PRINCIPAL,
        EstadoConversacion.CAPTURANDO_CANTIDAD: EstadoConversacion.SELECCIONANDO_PRODUCTO,
        EstadoConversacion.AGREGAR_MAS_O_CONTINUAR: (
            EstadoConversacion.CAPTURANDO_CANTIDAD
        ),
        EstadoConversacion.CAPTURANDO_DIRECCION: (
            EstadoConversacion.AGREGAR_MAS_O_CONTINUAR
        ),
        EstadoConversacion.SELECCIONANDO_MODIFICACION: (
            EstadoConversacion.REVISANDO_RESUMEN
        ),
    }
