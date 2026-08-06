## Objetivo

Crear el árbol de directorios documentado en `claude.md` para que cada archivo
posterior tenga un lugar evidente donde vivir.

## Estructura

```
src/
├── main.py              # entrada FastAPI
├── config.py            # settings con Pydantic BaseSettings
├── database.py          # engine y sesión async
├── models/              # SQLModel, una clase por tabla
├── schemas/             # Pydantic para request/response
├── api/                 # routers (webhook, admin, health)
├── whatsapp/            # client, signature, templates, messages
├── fsm/                 # states, transitions, handlers/
├── services/            # cliente_service, pedido_service, locks
├── notifications/       # telegram
└── utils/               # datetime, logging
tests/
├── conftest.py
├── unit/
└── integration/
docs/
n8n/workflows/
```

## Por qué esta separación

- `api/` solo traduce HTTP a llamadas de servicio; nada de lógica de negocio.
- `fsm/` no sabe de HTTP ni de httpx; recibe un mensaje normalizado y decide
  el siguiente estado. Eso lo hace testeable sin levantar servidor.
- `whatsapp/` es el único módulo que conoce el formato de Meta. Si mañana
  cambia la versión de la API, se toca un solo lugar.

## Criterio de aceptación

- [ ] Todos los directorios creados con su `__init__.py` (13 en total)
- [ ] `python -c "import src, src.models, src.fsm.handlers, src.whatsapp"` no truena
- [ ] La estructura coincide con la documentada en `claude.md`

Nota: `src/main.py` no se verifica aquí, se crea en el issue #12.
