from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_post_webhook_con_firma_invalida_devuelve_403():
    respuesta = client.post(
        "/webhook/whatsapp",
        content=b'{"entry": []}',
        headers={"X-Hub-Signature-256": "sha256=firma-que-nunca-va-a-coincidir"},
    )
    assert respuesta.status_code == 403
