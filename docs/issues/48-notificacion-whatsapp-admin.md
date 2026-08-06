## Depende de

- #13 — settings con `WHATSAPP_TELEFONO_ADMIN`
- #19 — cliente httpx sobre la Graph API (se reutiliza el mismo)

Bloqueo externo: registrar y aprobar la plantilla `handoff_asesor` en Meta
(categoría **utility**). Tarda de 1 hora a 3 días.

## Objetivo

Avisarle a Gabriel en tiempo real cuando una conversación necesita un humano.

## Por qué WhatsApp y no Telegram (decisión revisada 6-ago-2026)

Originalmente este issue usaba Telegram. Se cambió porque **Gabriel no usa
Telegram**: una notificación que llega a una app que el destinatario no abre no
sirve de nada, por muy simple que sea su API.

Se manda al **WhatsApp personal de Gabriel**, que es el que sí revisa. Ojo: no
es el número del bot — ese está en Cloud API y perdió la app móvil (issue #3).
Es un segundo número, el suyo de siempre, que recibe el aviso como cualquier
otro mensaje.

## Por qué tiene que ser plantilla, no texto libre

Gabriel nunca le escribe al bot, así que **nunca hay ventana de 24 h abierta
con él**. Fuera de ventana solo se pueden enviar plantillas aprobadas. No es
opcional.

Categoría **utility**: es una notificación transaccional sobre una operación en
curso. No usar lenguaje promocional en el copy o Meta la reclasifica a
marketing (5x más cara).

Costo: MX$0.1565 por handoff. Despreciable comparado con perder el cliente.

## Restricción de formato que condiciona el diseño

**Los parámetros de plantilla no admiten saltos de línea, tabs ni más de 4
espacios seguidos.** Eso mata la idea original de mandar los últimos 5 mensajes
de la conversación dentro del aviso: no caben en un parámetro.

Solución: la plantilla lleva solo los datos que sí caben en una línea cada uno.
El contexto completo se consulta en la base (o en el panel, cuando exista).

## Plantilla `handoff_asesor`

```
Cliente {{1}} necesita asesor.
Telefono: {{2}}
Motivo: {{3}}
Ultimo mensaje: {{4}}
```

| Var | Contenido | Ejemplo |
|---|---|---|
| `{{1}}` | nombre del cliente, o "sin registrar" | Restaurante El Buen Sabor |
| `{{2}}` | teléfono E.164 | +5214771234567 |
| `{{3}}` | motivo del escalamiento | 3 intentos invalidos en menu |
| `{{4}}` | último mensaje del cliente, truncado a 200 chars, saltos de línea reemplazados por espacio | oye necesito negociar el precio |

**Sanitizar `{{4}}` antes de enviar**: el texto viene del cliente y puede traer
saltos de línea. Sin limpiarlo, Meta rechaza el envío con error 132000.

## Implementación

`src/notifications/whatsapp_admin.py`, reutilizando el cliente httpx del
issue #19:

```
POST https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages
{
  "messaging_product": "whatsapp",
  "to": WHATSAPP_TELEFONO_ADMIN,
  "type": "template",
  "template": {
    "name": "handoff_asesor",
    "language": {"code": "es_MX"},
    "components": [{"type": "body", "parameters": [...]}]
  }
}
```

Vive en `notifications/` y no en `whatsapp/` porque es una decisión de negocio
(a quién se avisa y cuándo), no un detalle del protocolo de Meta.

## Manejo de fallas

Si el envío falla (plantilla no aprobada, número mal, rate limit), **se loguea
el error pero no se rompe el webhook**. El cliente ya quedó en
`EN_ASESOR_HUMANO` y guardado en base; que falle la notificación no debe
regresarlo al bot ni tumbar el request de Meta.

## Registro del mensaje

Como todo mensaje saliente, se guarda en `mensajes` con
`pricing_category='utility'` y su `costo_estimado`. Los handoffs cuentan para
el gasto mensual aunque no sean parte del flujo de pedido, y no deben
contaminar la métrica MSPC: se registran con `pedido_id` nulo.

## Criterio de aceptación

- [ ] Plantilla `handoff_asesor` aprobada por Meta en categoría utility
- [ ] Notificación llega al WhatsApp personal de Gabriel con nombre, teléfono,
      motivo y último mensaje
- [ ] `{{4}}` sanitizado: sin saltos de línea, truncado a 200 caracteres
- [ ] Una falla de envío no propaga excepción al webhook
- [ ] El fallo de notificación queda logueado para revisión manual
- [ ] El mensaje queda registrado en `mensajes` con categoría y costo
