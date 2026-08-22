from fastapi import FastAPI
from src.api.health import router as health_router
from src.api.webhook import router as webhook_router

app = FastAPI(title="Automatización WS Hielon", version ="0.1.0")
app.include_router(health_router)
app.include_router(webhook_router)