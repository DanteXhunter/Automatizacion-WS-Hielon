## Depende de

- #13 — `settings.database_url`

## Objetivo

Tener PostgreSQL corriendo en local y la base del proyecto creada.

## Instalación en macOS

```bash
brew install postgresql@16
brew services start postgresql@16
createdb hielon_dev
```

## Conexión

```
DATABASE_URL=postgresql+asyncpg://TU_USUARIO@localhost:5432/hielon_dev
```

El prefijo `postgresql+asyncpg://` le indica a SQLAlchemy qué driver usar.
Con `postgresql://` a secas intenta usar psycopg2, que es síncrono, y todo el
código async truena. Es un error frecuente y el mensaje no es obvio.

Alembic, en cambio, corre síncrono. Lo más simple es que las migraciones usen
una URL con `psycopg2` y la app use `asyncpg`, derivando una de la otra en
`env.py` (se resuelve en el issue #23).

## Por qué Postgres y no SQLite

Además de que el ERP futuro será relacional, este proyecto depende de dos
cosas que SQLite no tiene: **advisory locks** (issue #31) y **JSONB** con
índices para el contexto de la FSM.

## Criterio de aceptación

- [ ] Base `hielon_dev` creada
- [ ] Conexión verificada desde DBeaver o `psql`
- [ ] `DATABASE_URL` en el `.env` con el driver correcto
- [ ] `src/database.py` con el engine async y el generador de sesión
