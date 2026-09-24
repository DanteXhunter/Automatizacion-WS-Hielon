"""Notificación del handoff al responsable operativo."""

import logging
from uuid import uuid4

import pytest

from src.models.cliente import Cliente
from src.notifications import whatsapp_admin
from src.whatsapp.client import WhatsAppAPIError


def test_sanitizar_parametro_elimina_saltos_tabs_y_limita_longitud():
    texto = "primera línea\nsegunda\t   tercera " + ("x" * 250)

    limpio = whatsapp_admin.sanitizar_parametro(texto)

    assert "\n" not in limpio
    assert "\t" not in limpio
    assert "  " not in limpio
    assert len(limpio) == 200


@pytest.mark.asyncio
async def test_notificacion_envia_plantilla_y_registra_costo(monkeypatch):
    cliente = Cliente(
        id=uuid4(),
        telefono="+5214771234567",
        nombre="Restaurante Norte",
    )
    enviados = []

    class Sesion:
        def __init__(self):
            self.agregados = []
            self.commits = 0

        def add(self, mensaje):
            self.agregados.append(mensaje)

        async def commit(self):
            self.commits += 1

    class ClienteWhatsApp:
        async def enviar_plantilla(self, telefono, nombre, idioma, parametros):
            enviados.append((telefono, nombre, idioma, parametros))
            return "wamid.handoff"

    monkeypatch.setattr(
        whatsapp_admin.settings,
        "whatsapp_telefono_admin",
        "+5214777654321",
    )
    session = Sesion()

    enviado = await whatsapp_admin.notificar_handoff(
        session,
        ClienteWhatsApp(),
        cliente,
        motivo="Solicitud del cliente",
        ultimo_mensaje="quiero\nnegociar\t precio",
    )

    assert enviado is True
    assert enviados == [
        (
            "5214777654321",
            "handoff_asesor",
            "es_MX",
            [
                "Restaurante Norte",
                "+5214771234567",
                "Solicitud del cliente",
                "quiero negociar precio",
            ],
        )
    ]
    assert session.commits == 1
    assert session.agregados[0].whatsapp_message_id == "wamid.handoff"
    assert session.agregados[0].pricing_category == "utility"
    assert session.agregados[0].pedido_id is None


@pytest.mark.asyncio
async def test_falla_de_meta_se_loguea_y_no_se_propaga(monkeypatch, caplog):
    cliente = Cliente(id=uuid4(), telefono="+5214771234567")

    class ClienteWhatsApp:
        async def enviar_plantilla(self, *_args):
            raise WhatsAppAPIError("plantilla no aprobada", status_code=400)

    monkeypatch.setattr(
        whatsapp_admin.settings,
        "whatsapp_telefono_admin",
        "+5214777654321",
    )

    with caplog.at_level(logging.ERROR):
        enviado = await whatsapp_admin.notificar_handoff(
            object(),
            ClienteWhatsApp(),
            cliente,
            motivo="Solicitud del cliente",
            ultimo_mensaje="Necesito ayuda",
        )

    assert enviado is False
    assert "Falló la notificación de handoff" in caplog.text
