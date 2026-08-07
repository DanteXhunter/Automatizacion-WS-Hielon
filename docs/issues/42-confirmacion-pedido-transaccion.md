## Depende de

- #38 — botón Confirmar existente
- #41 — generación de folio
- #43 — validador de transiciones de estado

## Objetivo

Cerrar el pedido de forma atómica y avisarle al cliente.

## Operaciones, todas en UNA transacción

1. Validar que el borrador tenga al menos un item y una dirección
2. Recalcular el total sumando los `subtotal` de `pedido_items`
3. Generar el `numero_orden` (issue #41)
4. Cambiar `estado` de `borrador` a `pendiente`
5. Fijar `direccion_id` y `total`
6. Limpiar `conversaciones.pedido_borrador_id` y el contexto
7. Poner la conversación en `IDLE`

Todo o nada. Un pedido a medias, con folio pero sin total, o con estado
`pendiente` y una conversación que sigue creyendo que es borrador, es un
problema que solo se descubre cuando el repartidor ya salió.

## Mensaje de confirmación

**Cliente recurrente:**

```
¡Listo! Tu pedido #2026-0142 quedó registrado.
Total: $XXX. Te avisamos cuando vaya en camino.
```

**Cliente nuevo:** agregar horario de entrega estimado y que el pago es contra
entrega, para que sepa qué esperar.

## El envío va después del commit

Igual que en el dispatcher (issue #28): si el mensaje sale antes y la
transacción hace rollback, el cliente tiene un folio de un pedido que no
existe.

## Validaciones previas

| Situación | Acción |
|---|---|
| Borrador sin items | no confirmar, regresar a `SELECCIONANDO_PRODUCTO` |
| Borrador sin dirección | regresar a `CAPTURANDO_DIRECCION` |
| El pedido ya no está en `borrador` | ignorar, ya se confirmó (doble toque) |

El tercer caso importa: el cliente puede tocar "Confirmar" dos veces. La
segunda vez no debe generar un segundo pedido.

## Criterio de aceptación

- [ ] Todas las operaciones en una transacción
- [ ] El total se recalcula, no se confía en el acumulado
- [ ] Confirmar dos veces genera un solo pedido
- [ ] El mensaje incluye el folio y el total
- [ ] Cliente nuevo recibe la información adicional
- [ ] La conversación queda en `IDLE` sin borrador colgado
