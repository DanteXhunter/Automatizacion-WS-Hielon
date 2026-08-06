## Depende de

- #61 — n8n operativo con el timezone correcto

## Objetivo

Disparar el flujo de recordatorios matutinos automáticamente.

## Expresión cron

Lunes a sábado, 6:00 AM:

```
0 6 * * 1-6
```

`1-6` es lunes a sábado en la notación cron estándar (0 = domingo). Verificar
que n8n interprete los días con esa convención y no la ISO (donde lunes es 1
y domingo 7), porque cambia el resultado.

## Dependencia crítica: timezone

Ya se fijó `GENERIC_TIMEZONE=America/Mexico_City` en el issue #61. Sin eso,
el Cron Trigger de n8n interpreta "6:00" como **UTC**, y el recordatorio
saldría a las 12:00 del mediodía en León. Es el error más fácil de cometer
aquí y el más silencioso: el flow "funciona", solo que a la hora equivocada.

## Verificación

No esperar al día siguiente para confirmar: n8n permite ejecutar el nodo Cron
Trigger manualmente ("Execute Node") para probar el resto del flow sin
esperar a las 6 AM real. Para la hora exacta, revisar el log de ejecuciones
programadas durante al menos 2 días consecutivos antes de darlo por bueno.

## Criterio de aceptación

- [ ] El flow se dispara automáticamente lunes a sábado
- [ ] No se dispara en domingo
- [ ] Confirmado en el log de ejecuciones que la hora real coincide con las
      6:00 AM de León, no UTC
- [ ] Documentada la expresión cron y su significado en
      `docs/plantillas-hsm.md` o en el propio flow exportado
