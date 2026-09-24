# Hielon · Automatización de WhatsApp

Backend para recibir pedidos de hielo por WhatsApp, registrarlos en PostgreSQL y atender la conversación con una máquina de estados.

> **Estado:** en desarrollo. El webhook, el saludo, el menú y el flujo de armado del pedido se construyen sobre WhatsApp Cloud API oficial. La confirmación final, el despliegue y las automatizaciones proactivas aún no forman parte de una versión productiva.

## Qué contiene

- API FastAPI para el webhook de Meta y una ruta de salud.
- Validación de firma HMAC-SHA256 e idempotencia de mensajes entrantes.
- Máquina de estados para conducir la conversación.
- Persistencia de clientes, productos, pedidos, direcciones y mensajes en PostgreSQL.
- Cliente asíncrono `httpx` para responder mediante WhatsApp Cloud API.

Este repositorio es el backend conversacional. No incluye ERP, inventario, rutas de reparto ni una interfaz para asesores.

## Stack

| Área | Tecnología |
|---|---|
| Lenguaje y API | Python 3.12, FastAPI, Uvicorn |
| Datos | PostgreSQL, SQLModel, SQLAlchemy, asyncpg |
| Migraciones | Alembic |
| WhatsApp | Meta Cloud API, httpx |
| Pruebas | pytest, pytest-asyncio |

Las dependencias están declaradas en [`requirements.txt`](requirements.txt).

## Ejecutar localmente

Requisitos: Python 3.12, PostgreSQL y Git.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Crea una base PostgreSQL vacía y copia la configuración de ejemplo solo si aún no tienes un `.env`:

```bash
createdb hielon_dev
if [ ! -f .env ]; then cp .env.example .env; fi
```

Configura `DATABASE_URL` y las variables de WhatsApp en `.env`. Para una base local, la URL tiene este formato:

```text
postgresql+asyncpg://USUARIO:CONTRASEÑA@localhost:5432/hielon_dev
```

Después, aplica las migraciones, carga el catálogo inicial e inicia el servidor:

```bash
alembic upgrade head
python -m scripts.seed_productos
uvicorn src.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`.

| Ruta | Uso |
|---|---|
| `/health` | Estado básico del servicio. |
| `/docs` | Documentación interactiva de FastAPI. |
| `/webhook/whatsapp` | Verificación GET y recepción POST de eventos de Meta. |

## Configuración

Consulta [`.env.example`](.env.example) para la lista completa. Las variables principales son:

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Conexión PostgreSQL con el driver `asyncpg`. |
| `WHATSAPP_ACCESS_TOKEN` | Token de acceso a Cloud API. |
| `WHATSAPP_PHONE_NUMBER_ID` | Identificador del número conectado a Meta. |
| `WHATSAPP_VERIFY_TOKEN` | Token para verificar el webhook. |
| `WHATSAPP_APP_SECRET` | Clave para validar la firma de Meta. |

No guardes credenciales reales en Git ni compartas el contenido de `.env`. Los valores de ejemplo no permiten enviar mensajes.

## Pruebas

```bash
pytest -q
```

Las pruebas unitarias no necesitan conexión con Meta. Las pruebas de integración que usan PostgreSQL requieren `TEST_DATABASE_URL` y una base de pruebas migrada; sin esa variable, pytest las omite. Nunca apuntes esa variable a desarrollo o producción.

## Estructura

```text
src/api/          Endpoints HTTP
src/fsm/          Estados y handlers conversacionales
src/models/       Modelos SQLModel
src/services/     Persistencia y reglas de negocio
src/whatsapp/     Firma y cliente de Meta
alembic/          Migraciones de base de datos
scripts/          Tareas operativas
tests/            Pruebas unitarias y de integración
```

## Decisiones y documentación

- Se usa la API oficial de WhatsApp; no WhatsApp Web ni librerías no oficiales.
- Las conversaciones se procesan de forma determinista y se serializan por cliente con locks de PostgreSQL.
- Los precios iniciales del catálogo son provisionales (`$0.00 MXN`); no deben usarse como precios de venta.
- El contexto de negocio y las decisiones de arquitectura están en [`claude.md`](claude.md).

Todavía no se declara una licencia para este repositorio.
