## Depende de

- #5 — Phone Number ID y número de prueba
- #6 — token de acceso (o el temporal de 24 h para probar)
- #13 — settings cargando las credenciales
- #16 — webhook recibiendo para poder responder

## Objetivo

Enviar el primer mensaje saliente del bot: un echo que responda a quien
escriba.

## Alcance

`src/whatsapp/client.py`: wrapper async sobre httpx para Cloud API.

**Endpoint:**

```
POST https://graph.facebook.com/v21.0/{phone_number_id}/messages
Authorization: Bearer {access_token}
```

**Body de un mensaje de texto:**

```json
{
  "messaging_product": "whatsapp",
  "to": "5214771234567",
  "type": "text",
  "text": {"body": "Recibí tu mensaje"}
}
```

El campo `messaging_product` es obligatorio aunque parezca redundante.

## Requisitos de implementación

- Cliente `httpx.AsyncClient` reutilizado a nivel de aplicación, no uno nuevo
  por request (la reconexión TLS en cada mensaje es un desperdicio)
- Timeout explícito de 10 segundos
- Reintento con backoff exponencial ante 5xx y errores de red, máximo 3 intentos
- Sin reintento ante 4xx: son errores tuyos, reintentar no los arregla
- Loguear el `message_id` que devuelve Meta; se usa en Fase 2 para rastrear
  el estado de entrega

## Manejo de errores relevantes

| Código | Significado | Acción |
|---|---|---|
| 401 | Token inválido o expirado | Alertar, no reintentar |
| 429 | Rate limit | Backoff y reintentar |
| 470 | Fuera de la ventana de 24 h | Requiere plantilla, no texto libre |
| 5xx | Falla de Meta | Reintentar con backoff |

## Criterio de aceptación

- [ ] Se envía y recibe un mensaje de vuelta en el celular
- [ ] El `message_id` de Meta queda logueado
- [ ] Los errores 4xx se loguean con el cuerpo de la respuesta de Meta
- [ ] El token nunca aparece en los logs
