from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.health import router as health_router
from src.api.webhook import router as webhook_router
from src.config import settings
from src.whatsapp.client import WhatsAppClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Abre un cliente HTTP compartido y lo cierra al apagar la aplicación."""
    cliente_whatsapp = WhatsAppClient(
        access_token=settings.whatsapp_access_token.get_secret_value(),
        phone_number_id=settings.whatsapp_phone_number_id,
    )
    app.state.whatsapp_client = cliente_whatsapp

    try:
        yield
    finally:
        await cliente_whatsapp.aclose()


app = FastAPI(
    title="Automatización WS Hielon",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(health_router)
app.include_router(webhook_router)
