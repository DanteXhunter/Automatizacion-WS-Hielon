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


def test_mensaje_entrante_programa_respuesta_echo(monkeypatch):
    class ClienteWhatsAppFalso:
        def __init__(self) -> None:
            self.envios: list[tuple[str, str]] = []

        async def enviar_texto(self, destinatario: str, texto: str) -> str:
            self.envios.append((destinatario, texto))
            return "wamid.prueba"

    cliente_falso = ClienteWhatsAppFalso()

    async def registrar_mensaje_nuevo(_value, mensaje):
        return mensaje["from"]

    monkeypatch.setattr(webhook, "_registrar_mensaje_entrante", registrar_mensaje_nuevo)
    monkeypatch.setattr(
        app.state,
        "whatsapp_client",
        cliente_falso,
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
    assert cliente_falso.envios == [
        ("5214771234567", "Recibí tu mensaje"),
    ]
