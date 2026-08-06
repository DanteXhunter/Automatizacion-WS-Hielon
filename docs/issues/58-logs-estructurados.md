## Depende de

- #13 — nivel de log configurable desde settings

Se puede implementar desde Fase 1 si conviene; está en Fase 5 porque es
cuando se vuelve indispensable.

## Objetivo

Poder depurar producción sin acceso a una terminal interactiva pegada al
proceso.

## Formato

JSON, una línea por evento, con al menos:

```json
{
  "timestamp": "2026-08-15T10:32:01-06:00",
  "level": "INFO",
  "cliente_id": "uuid",
  "whatsapp_message_id": "wamid...",
  "estado_fsm": "CAPTURANDO_CANTIDAD",
  "evento": "transicion_exitosa",
  "mensaje": "..."
}
```

JSON en vez de texto libre porque en producción los logs se agregan (CloudWatch,
o simplemente `grep` + `jq` sobre el archivo) y buscar por campo estructurado
es mucho más rápido que parsear texto con regex.

## Prohibido loguear

- El token de acceso de Meta (`WHATSAPP_ACCESS_TOKEN`)
- El App Secret
- Contenido completo de mensajes que pudiera incluir datos sensibles del
  cliente, más allá de lo operativamente necesario

Es requisito de `claude.md` por LFPDPPP: no se guardan datos sensibles en
logs. El número de teléfono en sí se acepta porque es el identificador
operativo, pero no se loguean, por ejemplo, coordenadas exactas de ubicación
más allá de lo necesario para depurar un caso puntual.

## Implementación

Usar el módulo `logging` estándar con un formatter JSON (por ejemplo
`python-json-logger`), configurado una sola vez en `src/utils/logging.py` e
importado en todos los módulos. Nivel `INFO` en producción, `DEBUG` disponible
por variable de entorno para diagnóstico puntual.

## Criterio de aceptación

- [ ] Todos los logs salen en JSON con los campos mínimos
- [ ] Ningún secreto aparece en ningún log, verificado manualmente
- [ ] El nivel es configurable sin tocar código
- [ ] Los logs de un mismo `cliente_id` se pueden filtrar con `jq`
