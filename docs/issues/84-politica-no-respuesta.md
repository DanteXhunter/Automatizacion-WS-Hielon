## Depende de

- #80 — línea base medida

## Objetivo

Dejar de gastar mensajes en respuestas que no hacen avanzar el pedido.

**Delta de MSPC esperado: -0.5 a -1.5 en promedio**, concentrado en los pedidos
con errores, que son los caros.

## Regla general

**Un mensaje saliente solo se justifica si hace avanzar el pedido o evita que
el cliente se atore.** Todo lo demás es gasto.

## Casos

| Situación | Hoy | Propuesta |
|---|---|---|
| Entrada inválida | mensaje de error + reenviar el prompt (2 mensajes) | un solo mensaje: el prompt con la corrección incluida |
| Cliente manda un sticker o "ok" sin contexto | responde el menú | no responder |
| Cliente manda 3 mensajes seguidos rápido | responde a cada uno | esperar ~2s, responder una vez al último |
| Cliente escribe estando en `EN_ASESOR_HUMANO` | bot callado (ya correcto) | sin cambio |

## El caso del debounce

Un cliente que escribe "hola" / "buenas" / "quiero hielo" en tres mensajes
genera hoy tres respuestas. Con una espera corta antes de procesar, se responde
una sola vez.

Ojo: esto interactúa con los advisory locks del issue #31. **El lock serializa;
el debounce agrupa.** Son cosas distintas y ambas hacen falta: el lock evita
que dos mensajes corrompan el estado, el debounce evita pagar tres respuestas.

## Dónde está el límite

**No aplicar esto a costa de dejar al cliente sin saber qué hacer.** Si no
responder produce un "¿hola?" del cliente y luego sí hay que contestar, se
gastó lo mismo y se dio mala experiencia.

La prueba: si el cliente puede deducir el siguiente paso del mensaje que ya
tiene en pantalla, no hace falta otro. Si no, sí.

## Criterio de aceptación

- [ ] Entradas inválidas cuestan 1 mensaje, no 2
- [ ] Mensajes irrelevantes dentro de ventana no generan respuesta
- [ ] Debounce implementado y probado con 3 mensajes en menos de 2 segundos
- [ ] Ningún estado de la FSM queda sin salida por no responder
- [ ] MSPC re-medido
