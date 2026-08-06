## Depende de

- #16 — webhook que recibe los eventos `statuses`
- #64 — envíos que registrar

## Objetivo

Que cada plantilla enviada quede trazada en la misma tabla `mensajes` que usa
el backend, para tener una sola fuente de verdad de todo lo que se le mandó
a cada cliente.

## Al enviar

Insertar en `mensajes`:

```sql
INSERT INTO mensajes (cliente_id, direccion, whatsapp_message_id, tipo, contenido,
                      estado, pricing_category, costo_estimado, pedido_id)
VALUES ($cliente_id, 'saliente', $message_id, 'template', $payload_json,
        'sent', 'utility', $tarifa_utility_mxn, NULL);
```

El `whatsapp_message_id` es el que devuelve Meta en la respuesta del envío,
no uno inventado por n8n.

`costo_estimado` se guarda como **snapshot** con la tarifa vigente al momento
del envío, no se calcula después: las tarifas de Meta cambian y el histórico
de gasto debe seguir siendo correcto tras un cambio de precio.

`pedido_id` va en `NULL` porque el recordatorio no pertenece a ningún pedido
todavía. Si el cliente responde y termina comprando, ese pedido tendrá sus
propios mensajes; el recordatorio no debe contaminar la métrica MSPC.

## Categoría real, según Meta

El webhook de `statuses` incluye el objeto `pricing` con la categoría que Meta
**efectivamente cobró**. Puede no coincidir con la esperada: si Meta
reclasificó la plantilla a marketing, ahí se ve. Actualizar
`pricing_category` y `costo_estimado` con ese dato cuando llegue.

Esta es la fuente de verdad del dashboard de costos (Fase 6.1).

## Actualización del estado por webhooks de status

Meta manda al mismo webhook del backend eventos `statuses` (delivered, read,
failed) referenciando ese `whatsapp_message_id`. El backend ya distingue estos
eventos de los de `messages` (ver issue #16); falta el `UPDATE`:

```sql
UPDATE mensajes SET estado = $nuevo_estado
WHERE whatsapp_message_id = $message_id;
```

Esto no es parte del flow de n8n, es un ajuste al handler del webhook que se
beneficia de este issue: sin el registro inicial del envío, el `UPDATE` de
status no encontraría la fila a actualizar.

## Por qué importa el rastro completo

Si Gabriel pregunta por qué un cliente dice que nunca le llegó el
recordatorio, la tabla `mensajes` debe poder responder: se envió, se marcó
`failed` porque el número lo bloqueó, o nunca se intentó porque no tenía
opt-in.

## Criterio de aceptación

- [ ] Cada plantilla enviada por n8n genera un registro en `mensajes`
- [ ] El webhook del backend actualiza el `estado` al recibir el evento
      `statuses` correspondiente
- [ ] Un envío fallido queda visible con `estado = 'failed'`
- [ ] `pricing_category` y `costo_estimado` quedan poblados en cada envío
- [ ] La categoría se corrige si el webhook de status reporta una distinta
- [ ] Verificado con al menos un ciclo real: enviado, entregado, marcado
      `delivered`
