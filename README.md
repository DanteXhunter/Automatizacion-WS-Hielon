# Automatización de WhatsApp para Hielon de León

Backend en Python para atender conversaciones de WhatsApp de Hielon de León, registrar clientes y pedidos, y derivar los casos que requieren a una persona. El canal previsto es **WhatsApp Cloud API de Meta**; el flujo de pedido se construye con una máquina de estados determinista.

> **Estado del proyecto:** en desarrollo. El webhook, la validación de firma, el cliente HTTP de Meta, el esquema de datos, la deduplicación de mensajes y la base de la máquina de estados ya tienen código. Los handlers que capturan y confirman pedidos todavía no están conectados. El mensaje saliente actual es un echo provisional; no representa el flujo final de atención. Los precios del catálogo son provisionales (`0.00 MXN`) y no deben usarse para vender.

## Para qué existe

Hielon atiende a negocios y clientes de eventos que necesitan hielo en bolsas de 3, 5 o 10 kg. El objetivo de este backend es recibir solicitudes sin intervención humana en los casos normales, conservar el historial necesario para armar pedidos y avisar a un asesor cuando la conversación salga del flujo estándar. Más adelante enviará recordatorios matutinos únicamente a clientes con consentimiento documentado.

El repositorio contiene el **backend del bot**. Un ERP, un panel de chat para asesores y una interfaz administrativa completa serían proyectos separados. El modelo de datos deja espacio para integraciones futuras, pero la primera versión atiende solo a Hielon.

## Qué funciona hoy y qué falta

| Área | Estado actual |
|---|---|
| `GET /health` | Devuelve el estado básico de la aplicación. |
| `GET /webhook/whatsapp` | Responde al desafío de verificación de Meta cuando el token coincide. |
| `POST /webhook/whatsapp` | Comprueba la firma HMAC-SHA256 antes de interpretar el cuerpo, registra clientes y mensajes entrantes y descarta reintentos por `whatsapp_message_id`. |
| Mensajes salientes | Cliente `httpx` para Cloud API con timeout y reintentos ante fallos temporales. El webhook programa un echo solo para mensajes nuevos. La prueba con un teléfono real depende de la configuración de Meta. |
| Datos | Siete tablas SQLModel, una migración inicial de Alembic y un script idempotente para sembrar tres productos. |
| Conversación | Enum, mapa de transiciones, normalizador de entradas y dispatcher con persistencia antes del envío. Los handlers aún no se registran ni se invocan desde el webhook. |
| Operación futura | Están previstos la confirmación de pedidos, el control de horario, el handoff humano, los recordatorios con n8n, el despliegue en Railway y las métricas de costos. |

La máquina de estados no utiliza un modelo de lenguaje en la primera versión. Esto permite saber qué datos espera el bot en cada paso y rechazar transiciones no previstas.

## Arquitectura

```text
Cliente de WhatsApp
        │
        ▼
Meta Cloud API ── POST firmado ──► FastAPI /webhook/whatsapp
                                      │
                                      ├─ valida HMAC sobre los bytes originales
                                      ├─ identifica al cliente por teléfono
                                      ├─ inserta el mensaje si su ID es nuevo
                                      └─ programa el echo provisional
                                                │
                                                ▼
                                      cliente httpx → Meta Cloud API

PostgreSQL ◄── SQLModel / asyncpg ── servicios y dispatcher de conversación
                    ▲
                    └── Alembic / psycopg2 para migraciones
```

La deduplicación se apoya en un índice único de PostgreSQL, por lo que sigue funcionando con varios procesos. El dispatcher ya define que primero se guarda el nuevo estado y luego se envían mensajes; conectarlo al webhook y proteger los mensajes simultáneos del mismo cliente con advisory locks son pasos próximos.

### Modelo de datos

| Tabla | Propósito |
|---|---|
| `clientes` | Teléfono único, nombre y consentimiento básico para recordatorios. |
| `direcciones` | Direcciones de entrega por cliente. |
| `productos` | Presentaciones, peso, dimensiones, precio y disponibilidad. |
| `pedidos` | Estado, dirección, total y número de orden. |
| `pedido_items` | Cantidad y precio unitario conservado al crear cada pedido. |
| `conversaciones` | Estado actual y contexto temporal en `JSONB`. |
| `mensajes` | Historial entrante y saliente; el ID de Meta es único para evitar duplicados. |

El esquema describe el destino de la aplicación; que exista una tabla no significa que su flujo de negocio ya esté implementado. La migración inicial está en `alembic/versions/` y debe revisarse antes de aplicarse a una base con datos.

## Stack tecnológico

| Componente | Tecnología | Uso |
|---|---|---|
| API HTTP | Python 3.12, FastAPI, Uvicorn | Webhooks, verificación y documentación interactiva en `/docs`. |
| Configuración | Pydantic Settings | Lee y valida variables de entorno; mantiene secretos fuera del repositorio. |
| Persistencia | PostgreSQL, SQLModel, SQLAlchemy, `asyncpg` | Datos relacionales y sesiones asíncronas. |
| Migraciones | Alembic, `psycopg2-binary` | Versiona el esquema con una conexión síncrona derivada de `DATABASE_URL`. |
| Salida a WhatsApp | `httpx` | Llamadas asíncronas a Meta Cloud API. |
| Pruebas y estilo | pytest, pytest-asyncio, Black, Ruff | Pruebas de lógica, HTTP y base de datos; formato y lint. |
| Planeado | Railway, n8n | Despliegue y recordatorios programados; todavía no son requisitos para ejecutar localmente. |

`requirements.txt` declara las dependencias. Actualmente no fija versiones; antes de un despliegue reproducible habrá que establecerlas.

## Estructura del repositorio

```text
.
├── README.md                   # guía pública de uso y estado
├── claude.md                   # decisiones de negocio, arquitectura y roadmap
├── .env.example                # nombres de variables y valores de ejemplo
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py                  # toma DATABASE_URL y registra los modelos
│   └── versions/               # cambios versionados de esquema
├── scripts/
│   └── seed_productos.py       # catálogo inicial idempotente
├── src/
│   ├── main.py                 # ensamblaje y ciclo de vida de FastAPI
│   ├── config.py               # Settings
│   ├── database.py             # engine y fábrica de sesiones async
│   ├── api/                    # health y webhook
│   ├── models/                 # siete entidades SQLModel
│   ├── services/               # alta de clientes y registro de mensajes
│   ├── fsm/                    # estados, normalización y dispatcher
│   └── whatsapp/               # firma HMAC y cliente de Meta
└── tests/
    ├── unit/
    └── integration/
```

La estructura crece por fases: se agrega un módulo cuando el código que lo usa ya existe. `claude.md` es la fuente de decisiones y alcance; este README resume cómo arrancar y qué puede esperar alguien que llega al repositorio.

## Ejecutar en local

### Requisitos

- Python 3.12 y PostgreSQL local. Las instrucciones de instalación del servidor PostgreSQL varían según el sistema operativo; el proyecto usa PostgreSQL 16 durante el desarrollo.
- Una base de datos **vacía** para aplicar la migración inicial.
- Credenciales de Meta para probar envíos reales. Para desarrollar modelos, migraciones y pruebas locales bastan valores de ejemplo en las variables de WhatsApp.

Desde la raíz del repositorio:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
createdb hielon_dev
cp .env.example .env
```

Edita `.env`: coloca tu usuario y base reales en `DATABASE_URL` con el formato `postgresql+asyncpg://USUARIO@localhost:5432/hielon_dev`. Si PostgreSQL exige contraseña, inclúyela en la URL. No subas `.env` ni tokens al repositorio. La URL de `alembic.ini` se deja vacía a propósito; Alembic lee la misma configuración que la aplicación y cambia el driver a `psycopg2` durante la migración.

```bash
alembic upgrade head
python -m scripts.seed_productos
uvicorn src.main:app --reload
```

Abre `http://127.0.0.1:8000/health` para comprobar el proceso o `http://127.0.0.1:8000/docs` para ver los endpoints. Ejecutar el seed dos veces no duplica productos ni reemplaza precios que se hayan actualizado en la base.

**Si `hielon_dev` ya contiene tablas o Alembic indica una revisión desconocida**, detente antes de ejecutar `upgrade`, `downgrade` o limpiar el esquema. Crea otra base vacía, cambia `DATABASE_URL` en `.env` y aplica allí la migración. Las bases antiguas pueden contener datos que este repositorio no debe borrar automáticamente.

### Variables de entorno principales

| Variable | Uso |
|---|---|
| `DATABASE_URL` | Conexión PostgreSQL con driver `asyncpg`. |
| `WHATSAPP_ACCESS_TOKEN` | Token para mensajes salientes vía Meta. |
| `WHATSAPP_PHONE_NUMBER_ID` | ID del número registrado en Cloud API. |
| `WHATSAPP_VERIFY_TOKEN` | Valor acordado para el `GET` de verificación. |
| `WHATSAPP_APP_SECRET` | Clave usada para validar `X-Hub-Signature-256`. |
| `WHATSAPP_TELEFONO_ADMIN` | Número previsto para el handoff humano. |
| `HORA_INICIO`, `HORA_FIN`, `HORA_CORTE_MISMO_DIA`, `TIMEZONE` | Configuración de horario para fases siguientes. |
| `TARIFA_*_MXN`, `ALERTA_GASTO_MENSUAL_MXN` | Parámetros previstos para medir costos; revisar antes de usarlos en producción. |

Consulta `.env.example` para todos los nombres y valores de muestra. Los valores de ejemplo no autentican contra Meta.

## Pruebas

La suite habitual no requiere una cuenta de Meta:

```bash
pytest -q
black --check src/fsm src/services
ruff check src/fsm src/services
```

Hay archivos de la fase inicial que aún no siguen el formato actual de Black/Ruff; el chequeo global de estilo se habilitará después de normalizarlos.

La prueba de duplicados necesita una base PostgreSQL **exclusiva de tests** y omite su ejecución si no se define `TEST_DATABASE_URL`. Para correrla:

```bash
createdb hielon_test
DATABASE_URL=postgresql+asyncpg://USUARIO@localhost:5432/hielon_test alembic upgrade head
TEST_DATABASE_URL=postgresql+asyncpg://USUARIO@localhost:5432/hielon_test pytest -q tests/integration/test_webhook_idempotencia.py
```

Sustituye `USUARIO` por el usuario local de PostgreSQL. La prueba crea registros de prueba en esa base; no la apuntes a desarrollo ni producción. El cliente de Meta se sustituye por uno falso durante el test: no envía WhatsApps reales.

## Seguridad y límites de la versión actual

- El webhook verifica la firma sobre los bytes originales antes de procesar el JSON. Las firmas ausentes o inválidas reciben `403`.
- El teléfono se normaliza antes del alta; el ID único de mensaje evita que un reintento de Meta cree otra fila o programe otro echo.
- `.env` está ignorado por Git. No publiques secretos ni datos personales en ejemplos o logs.
- El echo actual es una respuesta de desarrollo. **No hay captura ni confirmación de pedidos operativa**, ni control de horario, opt-in completo, advisory locks o handoff humano funcional.
- La cuenta y el webhook de Meta deben configurarse para demostrar un envío real; las pruebas automatizadas usan dobles de prueba.

## Mantenimiento

Ejecuta las pruebas pertinentes antes de cambiar el comportamiento. Cualquier modificación de tablas o índices necesita una migración de Alembic. Mantén `.env` fuera del repositorio y actualiza este README o `claude.md` cuando cambie el comportamiento público o una decisión de arquitectura.

Este repositorio aún no incluye un archivo `LICENSE`; consulta al propietario antes de reutilizar o distribuir el código fuera del proyecto.

## Desarrollo previsto

Los siguientes componentes funcionales son el saludo y menú inicial, la serialización de mensajes por cliente y el control de horario laboral. Después se conectará la captura de pedidos con la persistencia y se comprobará el recorrido completo con pruebas de integración. La configuración de Meta para un envío real se realiza por separado.

Las decisiones de negocio y arquitectura están documentadas en [`claude.md`](claude.md).
