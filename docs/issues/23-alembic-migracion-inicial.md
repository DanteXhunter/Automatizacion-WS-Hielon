## Depende de

- #22 — modelos SQLModel definidos

## Objetivo

Versionar el esquema de la base de datos desde el primer día.

## Concepto

Alembic guarda el historial de cambios del esquema como archivos Python
versionados en git. Cada migración sabe subir (`upgrade`) y bajar
(`downgrade`). Así el esquema de producción se reconstruye exactamente igual
que el local, y cualquiera que clone el repo llega al mismo estado con un
comando.

**Regla del proyecto: cero `ALTER TABLE` manual.** Un cambio hecho a mano en
local que no quedó en una migración es un despliegue roto garantizado en
Fase 5.

## Configuración

```bash
alembic init alembic
```

En `alembic/env.py`:

1. Importar todos los modelos para que `target_metadata = SQLModel.metadata`
   los vea. Si un modelo no se importa, Alembic no lo detecta y lo omite en
   silencio.
2. Leer la URL desde `settings` en vez de dejarla escrita en `alembic.ini`,
   que se commitea.
3. Convertir la URL de `asyncpg` a `psycopg2`: Alembic corre síncrono.

## Generar

```bash
alembic revision --autogenerate -m "esquema inicial"
alembic upgrade head
```

**Siempre revisar el archivo generado antes de aplicarlo.** El autogenerate
falla con tipos personalizados y a veces genera un `drop_table` inesperado.

## Criterio de aceptación

- [ ] `alembic upgrade head` crea las 7 tablas desde una base vacía
- [ ] `alembic downgrade base` las elimina sin error
- [ ] La migración está commiteada
- [ ] `alembic.ini` no contiene credenciales
