## Depende de

- #10 — estructura de carpetas

## Objetivo

Fijar las dependencias, el contrato de configuración y evitar que se filtren
secretos al repositorio.

## requirements.txt

```
fastapi
uvicorn[standard]
gunicorn
sqlmodel
alembic
asyncpg
httpx
pydantic-settings
python-dotenv
pytest
pytest-asyncio
black
ruff
```

Fijar versiones con `pip freeze` una vez que todo corra, para que el despliegue
en EC2 (Fase 5) instale exactamente lo mismo que en local.

## .env.example

Todas las variables con valores dummy, sin un solo secreto real:

```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/hielon_dev
WHATSAPP_ACCESS_TOKEN=EAAxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=un_string_random_que_tu_inventas
WHATSAPP_APP_SECRET=abc123
TELEGRAM_BOT_TOKEN=123:ABC
TELEGRAM_CHAT_ID=123456
HORA_INICIO=07:00
HORA_FIN=17:00
HORA_CORTE_MISMO_DIA=14:00
TIMEZONE=America/Mexico_City
```

`WHATSAPP_VERIFY_TOKEN` lo inventas tú: es un string arbitrario que se
configura igual en Meta y en el `.env`, y sirve solo para el handshake inicial
del webhook. No lo confundas con `WHATSAPP_APP_SECRET`, que sí lo da Meta y es
el que firma cada request.

## .gitignore

```
.env
__pycache__/
*.pyc
.venv/
.DS_Store
.pytest_cache/
```

## Criterio de aceptación

- [ ] `pip install -r requirements.txt` funciona en un venv limpio
- [ ] `.env.example` documenta las 10 variables
- [ ] `.env` está ignorado y `git status` no lo muestra
- [ ] `.DS_Store` deja de aparecer como modificado
