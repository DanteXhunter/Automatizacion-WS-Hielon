## Depende de

- #6 — token permanente
- #7 — plantilla aprobada
- #63 — lista de destinatarios

## Objetivo

Entregar la plantilla `recordatorio_matutino` a cada cliente elegible.

## Llamada a Cloud API

```json
POST /v21.0/{phone_number_id}/messages
{
  "messaging_product": "whatsapp",
  "to": "{telefono_sin_signo_mas}",
  "type": "template",
  "template": {
    "name": "recordatorio_matutino",
    "language": {"code": "es_MX"},
    "components": [{
      "type": "body",
      "parameters": [{"type": "text", "text": "{nombre_del_cliente}"}]
    }]
  }
}
```

El nombre de la plantilla y el idioma deben coincidir exactamente con lo
aprobado en el issue #7, incluyendo mayúsculas.

## Envíos escalonados

Mandar los 100+ mensajes de golpe puede pegarle al rate limit de Meta (varía
según el tier de calidad de la cuenta). En n8n, usar el nodo **Loop Over
Items** con un **Wait** corto entre lotes (por ejemplo, 20 mensajes y pausa de
1 segundo) en vez de disparar todo en paralelo.

## Costo

Cada envío exitoso es una conversación **utility** de aproximadamente 0.033
USD. Con el flow corriendo diario, vale la pena que el resumen final (issue
#66) reporte cuántos se enviaron, para llevar cuenta del gasto mensual real
contra lo estimado.

## Criterio de aceptación

- [ ] La plantilla se envía con el nombre correcto como variable
- [ ] Los envíos van escalonados, no todos en un solo instante
- [ ] Se prueba primero contra 1-2 números de prueba antes de correr contra
      la lista completa
- [ ] El `message_id` de cada envío se captura para el issue #65
