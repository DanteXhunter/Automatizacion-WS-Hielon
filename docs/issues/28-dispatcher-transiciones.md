## Depende de

- #23 — tabla `conversaciones` creada
- #26 — mensajes normalizados y deduplicados
- #27 — enum de estados y mapa de transiciones

## Objetivo

Construir el enrutador que lleva cada mensaje entrante al handler del estado
en que se encuentra la conversación.

## Flujo del dispatcher

1. Recibir un mensaje ya normalizado (tipo, texto o payload de botón, cliente)
2. *(el advisory lock se inserta aquí en el issue #31; este issue se cierra
   sin él, dejando el punto de extensión marcado con un TODO)*
3. Cargar o crear la conversación de ese cliente
4. Resolver el handler correspondiente a `estado_actual`
5. Ejecutar el handler, que devuelve el próximo estado, el contexto
   actualizado y los mensajes a enviar
6. Validar que la transición sea legal según el mapa del issue #27
7. Persistir `estado_actual`, `estado_anterior`, `contexto` y
   `ultima_interaccion`
8. Commitear
9. **Después** del commit, enviar los mensajes salientes

## Por qué enviar después del commit

Si se envía el WhatsApp antes y la transacción falla, el cliente ya recibió
"¿cuántas bolsas?" mientras la base sigue creyendo que está en el menú. El
siguiente mensaje del cliente se interpretaría en el estado equivocado.

Al revés el error es benigno: si el envío falla después del commit, el estado
quedó guardado y el cliente puede volver a escribir.

## Contrato del handler

Cada handler es una función pura respecto de la infraestructura: recibe el
mensaje, el contexto y el cliente; devuelve un resultado. **No toca httpx ni
hace commit.** Así se testea sin base de datos ni red.

## Normalización de la entrada

El handler no debe saber si el cliente tocó un botón o escribió texto. El
dispatcher aplana el payload de Meta a algo como
`{tipo: "boton", valor: "hacer_pedido"}` o `{tipo: "texto", valor: "10"}`,
más `{tipo: "ubicacion", lat, lon}`.

## Criterio de aceptación

- [ ] El dispatcher resuelve el handler por estado
- [ ] Toda la persistencia ocurre en una sola transacción
- [ ] Los envíos salen después del commit
- [ ] Una transición inválida se loguea y no corrompe el estado
- [ ] Un estado sin handler registrado falla con error claro
