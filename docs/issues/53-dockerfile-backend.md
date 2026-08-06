> **Fase 5.1 — opcional, no bloquea producción (revisado 6-ago-2026).**
> Railway construye y despliega desde el repo sin Dockerfile. Este issue dejó
> de ser requisito para salir a producción y pasó a ser trabajo de aprendizaje
> y de portabilidad: sirve para no quedar amarrado a un proveedor y para
> levantar el stack completo en local. Hacerlo **después** de estar desplegado.

## Depende de

- #11 — `requirements.txt` con versiones fijas
- #52 — fundamentos entendidos
- #55 — **ya desplegado en Railway**; esto no lo reemplaza, lo respalda

## Objetivo

Empaquetar el backend en una imagen reproducible.

## Dockerfile multi-stage

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
RUN useradd --create-home appuser
WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY . .
RUN chown -R appuser:appuser /app
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 8000
CMD ["gunicorn", "src.main:app", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--workers", "4"]
```

## Por qué cada decisión

- **Multi-stage**: la etapa `builder` tiene herramientas de compilación que la
  imagen final no necesita cargar, reduce tamaño y superficie de ataque.
- **`python:3.12-slim`**, no `-alpine`: alpine usa musl en vez de glibc y
  algunas dependencias de compilación (asyncpg incluido) se complican ahí.
  Slim es el balance correcto para este proyecto.
- **Usuario no root** (`appuser`): si el contenedor se compromete, el atacante
  no queda con privilegios de root dentro de él.
- **`COPY requirements.txt .` antes de `COPY . .`**: mientras el código cambie
  pero las dependencias no, Docker reutiliza la capa del `pip install` y el
  build es mucho más rápido.
- **gunicorn + workers uvicorn**: gunicorn maneja el ciclo de vida de los
  procesos (reinicio si un worker muere), uvicorn ejecuta el código async.

## Criterio de aceptación

- [ ] `docker build` produce una imagen corriendo como `appuser`
- [ ] El contenedor responde `/health` al levantarlo
- [ ] Un cambio de código sin cambiar `requirements.txt` reconstruye rápido
      (verificar el caché de capas en el log del build)
- [ ] La imagen no incluye `.env` ni credenciales
