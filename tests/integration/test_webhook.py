import hashlib
import hmac
import sys
import types
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from src.api import webhook
from src.config import settings
from src.main import app
from src.models.cliente import Cliente
from src.models.conversacion import Conversacion

client = TestClient(app)


def test_post_webhook_con_firma_invalida_devuelve_403():
    respuesta = client.post(
        "/webhook/whatsapp",
        content=b'{"entry": []}',
        headers={"X-Hub-Signature-256": "sha256=firma-que-nunca-va-a-coincidir"},
    )
    assert respuesta.status_code == 403


def test_mensaje_entrante_programa_procesamiento_de_fsm(monkeypatch):
    cliente = Cliente(telefono="+5214771234567")
    procesados: list[tuple[str, str]] = []

    async def registrar_mensaje_nuevo(_value, mensaje):
        return cliente

    async def procesar(_cliente_whatsapp, cliente_recibido, mensaje):
        procesados.append((cliente_recibido.telefono, mensaje["id"]))

    monkeypatch.setattr(webhook, "_registrar_mensaje_entrante", registrar_mensaje_nuevo)
    monkeypatch.setattr(webhook, "_procesar_mensaje", procesar)
    monkeypatch.setattr(
        app.state,
        "whatsapp_client",
        object(),
        raising=False,
    )

    cuerpo = (
        b'{"entry":[{"changes":[{"value":{"messages":['
        b'{"id":"wamid.entrada","from":"5214771234567","type":"text"}'
        b"]}}]}]}"
    )
    secreto = settings.whatsapp_app_secret.get_secret_value()
    firma = (
        "sha256="
        + hmac.new(
            secreto.encode(),
            cuerpo,
            hashlib.sha256,
        ).hexdigest()
    )

    respuesta = client.post(
        "/webhook/whatsapp",
        content=cuerpo,
        headers={"X-Hub-Signature-256": firma},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "received"}
    assert procesados == [("+5214771234567", "wamid.entrada")]


@pytest.mark.asyncio
async def test_fuera_de_horario_no_invoca_fsm_y_limita_el_aviso(monkeypatch):
    cliente = Cliente(telefono="+5214771234567")
    session = object()

    class ContextoSesion:
        async def __aenter__(self):
            return session

        async def __aexit__(self, *_args):
            return False

    modulo_database = types.ModuleType("src.database")
    modulo_database.session_factory = lambda: ContextoSesion()
    monkeypatch.setitem(sys.modules, "src.database", modulo_database)
    monkeypatch.setattr(webhook, "es_horario_laboral", lambda: False)

    decisiones = iter([True, False])

    async def registrar(_session, _cliente):
        return next(decisiones)

    async def no_procesar(*_args, **_kwargs):
        raise AssertionError("La FSM no debe ejecutarse fuera de horario")

    envios = []

    class ClienteWhatsAppFalso:
        async def enviar_texto(self, telefono, texto):
            envios.append((telefono, texto))

    monkeypatch.setattr(webhook, "_registrar_aviso_fuera_de_horario", registrar)
    monkeypatch.setattr(webhook.dispatcher, "procesar", no_procesar)
    api = ClienteWhatsAppFalso()

    await webhook._procesar_mensaje(api, cliente, {"type": "text"})
    await webhook._procesar_mensaje(api, cliente, {"type": "text"})

    assert envios == [("5214771234567", webhook.AVISO_FUERA_DE_HORARIO)]


@pytest.mark.asyncio
async def test_aviso_fuera_de_horario_conserva_estado_y_contexto(monkeypatch):
    cliente = Cliente(telefono="+5214771234567")
    conversacion = Conversacion(
        cliente_id=cliente.id,
        estado_actual="CAPTURANDO_DIRECCION",
        contexto={"pedido_borrador_id": "pedido-1"},
    )

    class Resultado:
        def first(self):
            return conversacion

    class Sesion:
        commits = 0

        async def exec(self, _consulta):
            return Resultado()

        async def commit(self):
            self.commits += 1

        def add(self, _objeto):
            raise AssertionError("La conversación ya existe")

    @asynccontextmanager
    async def sin_lock(_session, _cliente_id):
        yield

    monkeypatch.setattr(webhook, "bloqueo_por_cliente", sin_lock)
    session = Sesion()
    instante = datetime(2026, 9, 27, 22, 0, tzinfo=ZoneInfo("America/Mexico_City"))

    primero = await webhook._registrar_aviso_fuera_de_horario(
        session, cliente, instante=instante
    )
    segundo = await webhook._registrar_aviso_fuera_de_horario(
        session, cliente, instante=instante + timedelta(minutes=30)
    )

    assert primero is True
    assert segundo is False
    assert conversacion.estado_actual == "CAPTURANDO_DIRECCION"
    assert conversacion.contexto["pedido_borrador_id"] == "pedido-1"
    assert session.commits == 2
