import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GRAPH_API_BASE_URL = "https://graph.facebook.com"
GRAPH_API_VERSION = "v21.0"
TIMEOUT_SEGUNDOS = 10.0
MAX_INTENTOS = 3


class WhatsAppAPIError(RuntimeError):
    """Representa un fallo controlado al comunicarse con Meta Cloud API."""

    def __init__(self, mensaje: str, status_code: int | None = None) -> None:
        super().__init__(mensaje)
        self.status_code = status_code


class WhatsAppClient:
    """Cliente asíncrono reutilizable para enviar mensajes por WhatsApp.

    Mantener una sola instancia permite que HTTPX reutilice las conexiones TCP
    y TLS entre mensajes. Crear un AsyncClient por cada webhook desperdiciaría
    tiempo en abrir una conexión nueva para cada respuesta.
    """

    def __init__(
        self,
        access_token: str,
        phone_number_id: str,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._access_token = access_token
        self._phone_number_id = phone_number_id
        self._sleeper = sleeper
        self._http = httpx.AsyncClient(
            base_url=GRAPH_API_BASE_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=TIMEOUT_SEGUNDOS,
            transport=transport,
        )

    async def enviar_texto(self, destinatario: str, texto: str) -> str:
        """Envía texto libre y devuelve el identificador asignado por Meta.

        Los errores temporales se reintentan hasta completar tres intentos. Un
        4xx distinto de 429 no se reintenta porque indica que la petición o las
        credenciales deben corregirse; repetirla sin cambios produciría el
        mismo resultado.

        Args:
            destinatario: Teléfono del cliente en formato internacional, sin
                el signo ``+``.
            texto: Contenido del mensaje que recibirá el cliente.

        Returns:
            El ``message_id`` que Meta asignó al mensaje.

        Raises:
            WhatsAppAPIError: Si Meta rechaza el mensaje, agota los reintentos
                o responde exitosamente sin incluir un ``message_id``.
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": destinatario,
            "type": "text",
            "text": {"body": texto},
        }
        return await self._enviar_payload(payload)

    async def enviar_interactivo(
        self, destinatario: str, interactivo: dict[str, Any]
    ) -> str:
        """Envía botones interactivos respetando los límites de Reply Buttons."""
        botones = interactivo.get("action", {}).get("buttons", [])
        if interactivo.get("type") != "button" or not 1 <= len(botones) <= 3:
            raise ValueError("Un menú interactivo requiere entre uno y tres botones.")
        identificadores = [boton["reply"]["id"] for boton in botones]
        titulos = [boton["reply"]["title"] for boton in botones]
        if len(set(identificadores)) != len(identificadores) or any(
            len(titulo) > 20 for titulo in titulos
        ):
            raise ValueError("Los IDs deben ser únicos y los títulos de máximo 20 caracteres.")

        return await self._enviar_payload(
            {
                "messaging_product": "whatsapp",
                "to": destinatario,
                "type": "interactive",
                "interactive": interactivo,
            }
        )

    async def _enviar_payload(self, payload: dict[str, Any]) -> str:
        """Comparte manejo de errores y reintentos entre texto y botones."""

        for intento in range(1, MAX_INTENTOS + 1):
            try:
                respuesta = await self._http.post(
                    f"/{GRAPH_API_VERSION}/{self._phone_number_id}/messages",
                    json=payload,
                )
            except httpx.RequestError as error:
                if intento == MAX_INTENTOS:
                    logger.error(
                        "Meta Cloud API no respondió después de %d intentos: %s",
                        intento,
                        self._ocultar_token(str(error)),
                    )
                    raise WhatsAppAPIError(
                        "No fue posible conectar con Meta Cloud API"
                    ) from error

                logger.warning(
                    "Error de red al llamar a Meta; reintento %d de %d",
                    intento + 1,
                    MAX_INTENTOS,
                )
                await self._esperar_backoff(intento)
                continue

            if respuesta.status_code == 429 or respuesta.status_code >= 500:
                if intento == MAX_INTENTOS:
                    logger.error(
                        "Meta agotó los reintentos | status=%d body=%s",
                        respuesta.status_code,
                        self._ocultar_token(respuesta.text),
                    )
                    raise WhatsAppAPIError(
                        "Meta Cloud API no pudo procesar el mensaje",
                        status_code=respuesta.status_code,
                    )

                logger.warning(
                    "Respuesta temporal de Meta | status=%d reintento=%d/%d",
                    respuesta.status_code,
                    intento + 1,
                    MAX_INTENTOS,
                )
                await self._esperar_backoff(intento)
                continue

            if respuesta.is_error:
                logger.error(
                    "Meta rechazó el mensaje sin reintento | status=%d body=%s",
                    respuesta.status_code,
                    self._ocultar_token(respuesta.text),
                )
                raise WhatsAppAPIError(
                    "Meta Cloud API rechazó el mensaje",
                    status_code=respuesta.status_code,
                )

            message_id = self._extraer_message_id(respuesta)
            logger.info("Mensaje enviado a Meta | message_id=%s", message_id)
            return message_id

        # El ciclo siempre devuelve o lanza una excepción. Esta guarda deja la
        # invariante explícita para lectores y analizadores de tipos.
        raise WhatsAppAPIError("No fue posible enviar el mensaje")

    async def aclose(self) -> None:
        """Cierra el pool de conexiones cuando termina la aplicación."""
        await self._http.aclose()

    async def _esperar_backoff(self, intento: int) -> None:
        """Espera 1 s tras el primer fallo y 2 s tras el segundo."""
        await self._sleeper(2 ** (intento - 1))

    def _extraer_message_id(self, respuesta: httpx.Response) -> str:
        """Valida la forma mínima de una respuesta exitosa de Meta."""
        try:
            contenido: Any = respuesta.json()
            message_id = contenido["messages"][0]["id"]
        except (KeyError, IndexError, TypeError, ValueError) as error:
            logger.error(
                "Meta respondió sin message_id | status=%d body=%s",
                respuesta.status_code,
                self._ocultar_token(respuesta.text),
            )
            raise WhatsAppAPIError(
                "Meta respondió exitosamente sin un message_id",
                status_code=respuesta.status_code,
            ) from error

        if not isinstance(message_id, str) or not message_id:
            raise WhatsAppAPIError(
                "Meta respondió con un message_id inválido",
                status_code=respuesta.status_code,
            )

        return message_id

    def _ocultar_token(self, texto: str) -> str:
        """Evita filtrar el access token aunque aparezca en una respuesta."""
        return texto.replace(self._access_token, "[REDACTADO]")
