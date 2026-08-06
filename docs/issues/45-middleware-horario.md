## Depende de

- #28 — dispatcher antes del cual se inserta
- #32 — `es_horario_laboral()`

## Objetivo

No atender pedidos fuera del horario laboral, sin perder el punto donde iba la
conversación.

## Comportamiento

Antes de invocar la FSM:

1. Guardar el mensaje entrante (siempre, sin importar la hora)
2. Si `es_horario_laboral()` es falso: responder el mensaje informativo y
   **terminar**, sin llamar al dispatcher
3. Si es horario laboral: seguir el flujo normal

La conversación **conserva su `estado_actual`**. Si el cliente iba en
`CAPTURANDO_DIRECCION` y escribe a las 22:00, al día siguiente retoma justo
ahí. Por eso `FUERA_DE_HORARIO` se modeló como condición y no como estado
(decisión cerrada en `claude.md`, issue #27).

## Mensaje

```
Gracias por escribirnos. Nuestro horario es de lunes a sábado de 7:00 a
17:00. Te atendemos en cuanto abramos.
```

## Texto libre o plantilla

Depende de la ventana de 24 horas:

- Si el cliente escribió hace menos de 24 h, la sesión está abierta y se puede
  mandar texto libre
- Si está cerrada, se requiere la plantilla `fuera_de_horario` (issue #8)

**Ambas opciones cuestan lo mismo** desde el 1-oct-2026: MX$0.1565 por mensaje,
categoría `service` o `utility` indistintamente. La ventana ya no decide el
precio, solo **qué formato** se puede enviar. Elegir texto libre es una
decisión de flexibilidad, no de ahorro.

Comprobar `conversaciones.ultima_interaccion` para decidir. La ventana la abre
el mensaje del **cliente**, y este mensaje que acaba de llegar la abre, así
que en la práctica casi siempre se puede responder con texto libre.

## Anti-spam básico

Si el cliente insiste fuera de horario, no responderle en cada mensaje: una
vez por ventana de varias horas basta. Se registra en el contexto cuándo se
mandó el último aviso. La versión completa está en el backlog (issue #74); en
v1 basta con no responder más de una vez por hora.

## Criterio de aceptación

- [ ] El middleware corre antes de la FSM
- [ ] Fuera de horario no se invoca ningún handler
- [ ] El `estado_actual` de la conversación no cambia
- [ ] El mensaje entrante sí se guarda
- [ ] Domingo se comporta como fuera de horario todo el día
- [ ] No se responde más de una vez por hora al mismo cliente
