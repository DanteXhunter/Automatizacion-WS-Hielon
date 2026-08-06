## Depende de

- #13 — settings con el token y chat_id de Telegram

Bloqueo externo: crear el bot con @BotFather y obtener el `chat_id` de
Gabriel. Es independiente de todo lo de Meta.

## Objetivo

Avisarle a Gabriel en tiempo real cuando una conversación necesita un humano.

## Por qué Telegram y no correo

Telegram tiene API simple (un POST con `httpx`, sin SMTP), notificación push
inmediata al celular, y no exige que el número de WhatsApp del bot pueda
recibir mensajes normales (que ya perdió, ver issue #3). Correo queda de
respaldo si Telegram falla.

## Implementación

`src/notifications/telegram.py`:

```
POST https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage
{
  "chat_id": TELEGRAM_CHAT_ID,
  "text": "..."
}
```

`TELEGRAM_CHAT_ID` se obtiene mandándole un mensaje al bot y consultando
`getUpdates` una vez, durante el setup.

## Contenido del mensaje

```
🔔 Cliente necesita asesor
Tel: +5214771234567 (Restaurante El Buen Sabor)
Motivo: 3 intentos inválidos en menú

Últimos mensajes:
[cliente] hola
[bot] ¿En qué te ayudo?
[cliente] oye necesito negociar el precio de mi pedido de mañana
```

Se incluyen los últimos 5 mensajes de la conversación, no solo el que
disparó el escalamiento; da contexto sin que Gabriel tenga que ir a revisar
la base.

## Manejo de fallas

Si Telegram no responde o el bot fue removido del chat, **se loguea el error
pero no se rompe el webhook**. El cliente ya quedó en `EN_ASESOR_HUMANO` y
guardado en base; que falle la notificación no debe regresarlo al bot ni
tumbar el request de Meta.

## Criterio de aceptación

- [ ] Notificación llega al Telegram de Gabriel con teléfono, motivo y
      últimos mensajes
- [ ] Una falla de Telegram no propaga excepción al webhook
- [ ] El fallo de notificación queda logueado para revisión manual
- [ ] Probado con el chat_id real de Gabriel
