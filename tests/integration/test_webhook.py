import hashlib
import hmac

from fastapi.testclient import TestClient

from src.api import webhook
from src.config import settings
from src.main import app

client = TestClient(app)


def test_post_webhook_con_firma_invalida_devuelve_403():
    respuesta = client.post(
        "/webhook/whatsapp",
        content=b'{"entry": []}',
        headers={"X-Hub-Signature-256": "sha256=firma-que-nunca-va-a-coincidir"},
    )
    assert respuesta.status_code == 403


def test_mensaje_entrante_programa_procesamiento_de_fsm(monkeypatch):
    from src.models.cliente import Cliente

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
