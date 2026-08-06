## Depende de

- #12 — app FastAPI existente

Se cierra con `curl` mandando un payload de ejemplo; no requiere que Meta esté
configurado.

## Objetivo

Recibir los eventos de Meta y registrarlos, sin procesarlos todavía.

## Regla no negociable

**Responder 200 siempre y en menos de 5 segundos.**

Si tardas más o devuelves error, Meta reintenta el mismo evento con backoff, y
si el patrón persiste **desactiva tu webhook**. Recuperarlo es manual desde el
panel.

Consecuencia de diseño: el endpoint acusa recibo de inmediato y el trabajo
pesado (base de datos, llamadas a Meta) va fuera de la ruta crítica, con
`BackgroundTasks` de FastAPI. Cualquier excepción se atrapa y se loguea, pero
el status sigue siendo 200.

## Estructura del payload

Meta anida bastante. Un mensaje de texto llega así:

```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WABA_ID",
    "changes": [{
      "field": "messages",
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {"phone_number_id": "..."},
        "contacts": [{"profile": {"name": "Cristopher"}, "wa_id": "5214771234567"}],
        "messages": [{
          "from": "5214771234567",
          "id": "wamid.HBgN...",
          "timestamp": "1730000000",
          "type": "text",
          "text": {"body": "hola"}
        }]
      }
    }]
  }]
}
```

Notas: `entry` y `changes` son listas y pueden traer varios eventos en un solo
request. El `wa_id` viene **sin** el signo `+`. El campo `messages` puede no
existir: los eventos de cambio de estado (`statuses`) llegan al mismo endpoint.

## Criterio de aceptación

- [ ] Devuelve 200 en todos los casos, incluso con payload malformado
- [ ] Loguea el body crudo completo para inspección
- [ ] Distingue eventos con `messages` de los que traen `statuses`
- [ ] Un payload inesperado no tira una excepción sin capturar
