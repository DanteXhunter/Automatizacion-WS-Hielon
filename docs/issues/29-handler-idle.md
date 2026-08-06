## Depende de

- #25 — identificación del cliente
- #28 — dispatcher que enrute a este handler

## Objetivo

Implementar el punto de entrada de toda conversación.

## Comportamiento

Al llegar cualquier mensaje con la conversación en `IDLE`:

1. Determinar si el cliente es conocido (tiene nombre o pedidos previos)
2. Enviar el saludo correspondiente junto con el menú principal
3. Transicionar a `MENU_PRINCIPAL`

## Mensajes

**Cliente conocido:**

```
¡Hola de nuevo, {nombre}! ¿En qué te ayudo hoy?
```

**Cliente nuevo:**

```
¡Hola! Soy el asistente de pedidos de Hielon de León.
Te ayudo a levantar tu pedido de hielo en unos pasos.
```

El contenido del mensaje **no se ignora**: si el cliente escribió
"quiero 10 bolsas", en v1 igual se le muestra el menú (la FSM es determinista,
no interpreta lenguaje natural). Está en el backlog resolverlo con LLM.

## Alta implícita del cliente

Si el teléfono no existe, `cliente_service` (issue #25) lo crea aquí. El
`opt_in_recordatorios` queda en FALSE: escribir al bot **no es** consentimiento
para recibir mensajes proactivos. Eso se pide aparte con la plantilla del
issue #8.

## Criterio de aceptación

- [ ] Cliente nuevo recibe el saludo de bienvenida y queda registrado
- [ ] Cliente conocido recibe el saludo personalizado con su nombre
- [ ] En ambos casos se envía el menú y se queda en `MENU_PRINCIPAL`
- [ ] `opt_in_recordatorios` permanece en FALSE
- [ ] Un mensaje de tipo imagen o audio en `IDLE` no truena: se saluda igual
