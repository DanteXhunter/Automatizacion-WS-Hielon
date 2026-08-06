## Depende de

- #54 — compose que se documenta
- #55 — servidor donde se prueban los procedimientos

## Objetivo

Que el proyecto sobreviva sin que el desarrollador original tenga que estar
presente.

## Contenido de docs/deployment.md

1. **Despliegue de una versión nueva**: pull del código, rebuild de la imagen
   del backend, `docker compose up -d --build`, verificación de `/health`
2. **Rollback**: cómo volver a la imagen anterior si algo sale mal
   (mantener el tag de la imagen previa antes de sobreescribir `latest`)
3. **Respaldo de Postgres**:
   ```bash
   docker exec -t postgres pg_dump -U user hielon > backup_$(date +%F).sql
   ```
   Con qué frecuencia correrlo (sugerido: diario, vía cron en el host) y dónde
   almacenar el respaldo (fuera de la misma instancia EC2, para que un
   problema con la instancia no se lleve también el backup)
4. **Restauración**: `psql -U user hielon < backup.sql` contra una instancia
   limpia, y en qué orden validar que todo volvió (migraciones al día,
   conteo de tablas)
5. **Rotación del token de Meta**: cómo generar uno nuevo desde el System
   User sin tumbar el servicio (generar el nuevo, actualizar el `.env`,
   reiniciar el backend, revocar el viejo)

## Por qué esto no es opcional para un proyecto de portafolio

Un runbook demuestra que el proyecto se pensó para operar, no solo para
funcionar una vez en la demo. Es de las piezas que un revisor técnico nota.

## Criterio de aceptación

- [ ] `docs/deployment.md` cubre los 5 puntos
- [ ] El procedimiento de respaldo se probó al menos una vez de punta a punta
      (respaldar y restaurar en una base de prueba)
- [ ] Un tercero podría seguir el documento sin preguntar nada al desarrollador
