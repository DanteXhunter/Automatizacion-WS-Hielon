## Depende de

- #23 — migraciones que correr contra el Postgres del contenedor
- #53 — imagen del backend

## Objetivo

Levantar Postgres, backend y n8n coordinados con un solo comando.

## docker-compose.yml

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: hielon
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: .
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8000:8000"

  n8n:
    image: n8nio/n8n
    env_file: .env
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
  n8n_data:
```

## Puntos importantes

- **`depends_on` con `condition: service_healthy`**: sin esto, `depends_on` a
  secas solo espera a que el contenedor arranque, no a que Postgres esté listo
  para aceptar conexiones. El backend fallaría en su primer intento de
  conexión con un `depends_on` simple.
- **Los secretos vienen de `.env` vía `env_file`**, nunca escritos en el
  propio `docker-compose.yml`, que sí se commitea.
- **Volúmenes nombrados** para Postgres y n8n: sin ellos, `docker compose
  down` borra los datos.
- Dentro de la red de compose, el backend se conecta a Postgres por el nombre
  del servicio: `postgresql+asyncpg://user:pass@postgres:5432/hielon`, no
  `localhost`.

## Criterio de aceptación

- [ ] `docker compose up` levanta los tres servicios sanos
- [ ] El backend espera a que Postgres esté healthy antes de conectar
- [ ] `docker compose down` (sin `-v`) conserva los datos al volver a subir
- [ ] Ningún secreto está escrito directamente en el compose
