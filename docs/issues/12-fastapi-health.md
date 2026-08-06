## Depende de

- #11 — dependencias instaladas

## Objetivo

Tener la aplicación FastAPI mínima corriendo en local.

## Alcance

- `src/main.py` con la instancia de FastAPI, título y versión
- `src/api/health.py` con un router que expone `GET /health`
- Router incluido desde `main.py`

Respuesta esperada:

```json
{"status": "ok", "version": "0.1.0"}
```

## Comando de arranque

```bash
uvicorn src.main:app --reload --port 8000
```

El flag `--reload` reinicia el servidor al guardar un archivo. Solo para
desarrollo: en producción se usa gunicorn con workers uvicorn (Fase 5).

## Por qué un endpoint de health

No es decorativo. Lo usa Railway (Fase 5) para saber si el servicio quedó
vivo antes de mandarle tráfico, y es lo primero que se consulta al depurar un
deploy. Debe ser
barato: no consulta la base de datos ni llama a Meta.

## Criterio de aceptación

- [ ] `GET /health` devuelve 200 con el JSON esperado
- [ ] `GET /docs` renderiza el Swagger autogenerado
- [ ] El servidor levanta sin warnings
