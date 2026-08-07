from fastapi import FastAPI
from src.api.health import router

app = FastAPI(title="Automatización WS Hielon", version ="0.1.0")
app.include_router(router)