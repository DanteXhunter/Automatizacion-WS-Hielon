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
INSERT INTO mensajes (cliente_id, direccion, whatsapp_message_id, tipo, contenido, estado)
VALUES ($cliente_id, 'saliente', $message_id, 'template', $payload_json, 'sent');
```

El `whatsapp_message_id` es el que devuelve Meta en la respuesta del envío,
no uno inventado por n8n.

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
- [ ] Verificado con al menos un ciclo real: enviado, entregado, marcado
      `delivered`
