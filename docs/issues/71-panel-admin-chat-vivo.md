## Idea de backlog

Interfaz web con chat en vivo (WebSockets o Server-Sent Events) para que un
humano pueda responder directamente desde el mismo número del bot.

## Por qué resuelve un problema real

Es la respuesta de largo plazo a la limitación central del proyecto: al
registrar el número en Cloud API se pierde el acceso desde la app móvil de
WhatsApp Business (ver issue #3). En v1 el handoff se resuelve con una
notificación al WhatsApp personal de Gabriel, pero un humano no puede "tomar"
la conversación desde ahí;
solo se entera y decide qué hacer por fuera. Un panel con chat en vivo
cerraría ese ciclo completo dentro del mismo sistema.

## Por qué no en v1

`claude.md` es explícito: sin panel admin React en v1, visualización vía
Swagger y DBeaver. Es la pieza de mayor esfuerzo del backlog completo; se
reconsidera cuando el volumen de handoffs justifique la inversión.
