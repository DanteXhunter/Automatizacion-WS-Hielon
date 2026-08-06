## Depende de

- #13 — settings con las horas configurables

## Objetivo

Concentrar toda la lógica de tiempo en un solo módulo con una sola fuente de
verdad.

## Alcance

`src/utils/datetime.py`:

```python
def ahora_local() -> datetime          # datetime con tz America/Mexico_City
def es_horario_laboral(dt=None) -> bool
def paso_hora_corte(dt=None) -> bool   # después de las 14:00
def es_dia_habil(dt=None) -> bool      # lunes a sábado
```

## Reglas de negocio

- Horario: lunes a sábado, 7:00 a 17:00
- Domingo: cerrado todo el día
- Hora de corte para pedidos del mismo día: 14:00

Los valores vienen de `settings`, no hardcodeados: Gabriel puede cambiar el
horario sin tocar código.

## Timezone

Usar `zoneinfo.ZoneInfo("America/Mexico_City")`, de la librería estándar desde
Python 3.9. No usar `pytz`.

**Trampa:** `datetime.now()` sin timezone devuelve la hora del sistema. En el
contenedor de Docker (Fase 5) eso es **UTC**, que va 6 horas adelante de León.
Un cliente escribiendo a las 12:00 del mediodía sería rechazado por "fuera de
horario" porque el servidor cree que son las 18:00. Toda comparación de hora
debe pasar por `ahora_local()`.

México eliminó el horario de verano en 2022, así que el offset es fijo, pero
usar `ZoneInfo` protege ante cambios futuros de legislación.

## Criterio de aceptación

- [ ] Todas las funciones usan `ZoneInfo`, ninguna usa `datetime.now()` pelón
- [ ] Los valores se leen de `settings`
- [ ] Tests de los bordes: 06:59, 07:00, 13:59, 14:00, 16:59, 17:00
- [ ] Test de domingo cerrado
- [ ] Tests que pasen aunque el reloj del sistema esté en UTC
