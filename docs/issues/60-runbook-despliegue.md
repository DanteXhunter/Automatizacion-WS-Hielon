## Depende de

- #55 — servicio en Railway donde se prueban los procedimientos

## Objetivo

Que el proyecto sobreviva sin que el desarrollador original tenga que estar
presente.

## Contenido de docs/deployment.md

1. **Despliegue de una versión nueva**: `git push` a `main`; Railway
   reconstruye y reinicia solo. Verificar `/health` y los logs del deploy.
2. **Rollback**: Railway > Deployments > el deploy anterior > **Redeploy**.
   No hay que manejar tags de imágenes a mano.
3. **Respaldo de Postgres**:
   ```bash
   pg_dump "$DATABASE_URL_PUBLICA_RAILWAY" > backup_$(date +%F).sql
   ```
   Railway hace sus propios backups, pero **un backup que solo vive en el
   mismo proveedor no es un backup**: si se pierde la cuenta, se pierde todo.
   Correr este dump semanalmente y guardarlo fuera de Railway.
4. **Restauración**: `psql -U user hielon < backup.sql` contra una instancia
   limpia, y en qué orden validar que todo volvió (migraciones al día,
   conteo de tablas)
5. **Rotación del token de Meta**: cómo generar uno nuevo desde el System
   User sin tumbar el servicio (generar el nuevo, actualizarlo en Variables de
   Railway, esperar el redeploy automático, revocar el viejo)

## Por qué esto no es opcional para un proyecto de portafolio

Un runbook demuestra que el proyecto se pensó para operar, no solo para
funcionar una vez en la demo. Es de las piezas que un revisor técnico nota.

## Criterio de aceptación

- [ ] `docs/deployment.md` cubre los 5 puntos
- [ ] El procedimiento de respaldo se probó al menos una vez de punta a punta
      (respaldar y restaurar en una base de prueba)
- [ ] Un tercero podría seguir el documento sin preguntar nada al desarrollador
