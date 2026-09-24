import logging

import httpx
import pytest

from src.whatsapp.client import WhatsAppAPIError, WhatsAppClient

TOKEN_PRUEBA = "token-super-secreto"
PHONE_NUMBER_ID_PRUEBA = "123456789"


async def no_esperar(_: float) -> None:
    """Sustituye asyncio.sleep para que los reintentos no ralenticen tests."""


@pytest.mark.asyncio
async def test_envio_exitoso_devuelve_message_id_y_payload_correcto():
    async def responder(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v21.0/123456789/messages"
        assert request.headers["Authorization"] == f"Bearer {TOKEN_PRUEBA}"
        assert request.content == (
            b'{"messaging_product":"whatsapp","to":"5214771234567",'
            b'"type":"text","text":{"body":"Recibi tu mensaje"}}'
        )
        return httpx.Response(200, json={"messages": [{"id": "wamid.123"}]})

    cliente = WhatsAppClient(
        TOKEN_PRUEBA,
        PHONE_NUMBER_ID_PRUEBA,
        transport=httpx.MockTransport(responder),
        sleeper=no_esperar,
    )

    try:
        message_id = await cliente.enviar_texto(
            "5214771234567",
            "Recibi tu mensaje",
        )
    finally:
        await cliente.aclose()

    assert message_id == "wamid.123"


@pytest.mark.asyncio
async def test_429_y_5xx_se_reintentan_con_backoff():
    intentos = 0
    esperas: list[float] = []

    async def responder(_: httpx.Request) -> httpx.Response:
        nonlocal intentos
        intentos += 1
        if intentos == 1:
            return httpx.Response(429, json={"error": "rate limit"})
        if intentos == 2:
            return httpx.Response(503, json={"error": "no disponible"})
        return httpx.Response(200, json={"messages": [{"id": "wamid.456"}]})

    async def registrar_espera(segundos: float) -> None:
        esperas.append(segundos)

    cliente = WhatsAppClient(
        TOKEN_PRUEBA,
        PHONE_NUMBER_ID_PRUEBA,
        transport=httpx.MockTransport(responder),
        sleeper=registrar_espera,
    )

    try:
        message_id = await cliente.enviar_texto("5214771234567", "Hola")
    finally:
        await cliente.aclose()

    assert message_id == "wamid.456"
    assert intentos == 3
    assert esperas == [1, 2]


@pytest.mark.asyncio
async def test_4xx_no_se_reintenta_y_el_token_no_aparece_en_logs(caplog):
    intentos = 0

    async def responder(_: httpx.Request) -> httpx.Response:
        nonlocal intentos
        intentos += 1
        return httpx.Response(
            401,
            json={"error": f"token inválido: {TOKEN_PRUEBA}"},
        )

    cliente = WhatsAppClient(
        TOKEN_PRUEBA,
        PHONE_NUMBER_ID_PRUEBA,
        transport=httpx.MockTransport(responder),
        sleeper=no_esperar,
    )

    with caplog.at_level(logging.ERROR), pytest.raises(WhatsAppAPIError) as error:
        await cliente.enviar_texto("5214771234567", "Hola")

    await cliente.aclose()

    assert error.value.status_code == 401
    assert intentos == 1
    assert TOKEN_PRUEBA not in caplog.text
    assert "[REDACTADO]" in caplog.text


@pytest.mark.asyncio
async def test_error_de_red_se_reintenta_tres_veces():
    intentos = 0

    async def fallar(request: httpx.Request) -> httpx.Response:
        nonlocal intentos
        intentos += 1
        raise httpx.ConnectError("sin conexión", request=request)

    cliente = WhatsAppClient(
        TOKEN_PRUEBA,
        PHONE_NUMBER_ID_PRUEBA,
        transport=httpx.MockTransport(fallar),
        sleeper=no_esperar,
    )

    try:
        with pytest.raises(WhatsAppAPIError) as error:
            await cliente.enviar_texto("5214771234567", "Hola")
    finally:
        await cliente.aclose()

    assert "conectar" in str(error.value)
    assert intentos == 3
