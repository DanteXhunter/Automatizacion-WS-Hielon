## Depende de

- #32 — `paso_hora_corte()`
- #38 — mensaje de resumen al que se antepone la nota

## Objetivo

Administrar la expectativa de entrega cuando el pedido entra después de la
hora de corte.

## Contexto

La hora de corte para entregas del mismo día son las **14:00**. Después de
eso, la ruta del día ya está armada y probablemente el pedido no alcanza.

Regla de negocio de `claude.md`: el bot **sugiere**, no decide. Si el cliente
insiste, la decisión final es humana.

## Comportamiento en v1

En `REVISANDO_RESUMEN`, si `paso_hora_corte()`:

```
Ya pasó nuestro horario de corte de las 2 PM, así que este pedido
probablemente saldría mañana temprano. Si lo necesitas hoy, con gusto te
comunicamos con un asesor.
```

El pedido **se confirma normal** y queda en `pendiente`. No se bloquea la
confirmación ni se fuerza `fecha_entrega`.

## Por qué no se programa automáticamente

Programar de verdad implica el estado `programado`, definir la fecha, y que
alguien del negocio revise esos pedidos por la mañana. Ese flujo completo está
en el backlog (issue #69). Prometer una entrega programada sin el proceso
detrás es peor que solo advertirlo.

## Interacción con el horario laboral

El corte de las 14:00 es distinto del cierre de las 17:00. Entre 14:00 y 17:00
el bot atiende normal, solo agrega esta nota. Después de las 17:00 aplica el
middleware del issue #45 y ni siquiera se llega aquí.

## Criterio de aceptación

- [ ] La nota aparece solo entre 14:00 y 17:00 en día hábil
- [ ] Antes de las 14:00 no aparece
- [ ] El pedido se confirma igual, en estado `pendiente`
- [ ] La hora de corte se lee de `settings`, no hardcodeada
- [ ] Tests en 13:59 y 14:01
