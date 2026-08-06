## Depende de

- #38 — resumen que transiciona hacia aquí

## Objetivo

Evitar cancelaciones accidentales con una confirmación explícita.

## Mensaje

```
¿Seguro que deseas cancelar tu pedido?
```

Botones: `Sí, cancelar` / `No, regresar`

## Transiciones

| Entrada | Efecto | Destino |
|---|---|---|
| `si_cancelar` | pedido borrador pasa a `cancelado_cliente` | `IDLE` |
| `no_regresar` | nada | `REVISANDO_RESUMEN` |

## Al cancelar

1. Cambiar `pedidos.estado` de `borrador` a `cancelado_cliente`
2. Limpiar `conversaciones.pedido_borrador_id` y el contexto
3. Enviar despedida:

```
Listo, cancelamos tu pedido. Aquí estamos cuando nos necesites.
```

## Por qué no se borra el pedido

Se marca como cancelado, no se elimina. Sirve para dos cosas: saber en qué
punto del flujo abandona la gente (dato de producto) y tener rastro si el
cliente reclama que sí pidió. `pedido_items` se conserva por la misma razón.

## Sin transición "atrás"

Este estado no tiene botón Volver: el botón "No, regresar" ya cumple esa
función. Está documentado así en `claude.md`.

## Criterio de aceptación

- [ ] Sí cancela, marca `cancelado_cliente` y limpia la conversación
- [ ] No regresa al resumen con el pedido intacto
- [ ] El pedido cancelado sigue en la base con sus items
- [ ] `pedido_borrador_id` queda en NULL tras cancelar
- [ ] Una entrada que no sea ninguno de los dos botones repite la pregunta,
      nunca asume cancelar
