## Depende de

- #16 — webhook recibiendo eventos
- #23 — tabla `mensajes` creada
- #25 — el mensaje se asocia a un cliente

## Objetivo

Garantizar que el mismo evento de Meta no se procese dos veces.

## Contexto

Meta reintenta la entrega si no recibe 200 dentro de su ventana de tiempo. Un
webhook que tardó 6 segundos por una consulta lenta puede llegar dos o tres
veces. Sin protección, el resultado es: dos mensajes duplicados en la
conversación, la FSM avanzando dos pasos y potencialmente dos pedidos.

**Idempotencia**: que repetir la operación no produzca efecto adicional.

## Implementación

Cada mensaje trae un `id` único y estable: `wamid.HBgNNTIx...`

1. Constraint `UNIQUE` en `mensajes.whatsapp_message_id`
2. Al recibir, `INSERT ... ON CONFLICT (whatsapp_message_id) DO NOTHING`
3. Si el INSERT no afectó filas, es duplicado: se responde 200 y **no se
   invoca la FSM**

La verificación va contra la base de datos, no contra un set en memoria: con
varios workers de gunicorn (Fase 5) cada proceso tendría su propio set y el
duplicado se colaría.

## Punto sutil

El descarte debe ocurrir **antes** de ejecutar cualquier efecto: antes de
avanzar la FSM y antes de enviar la respuesta al cliente. Un duplicado
detectado después de mandar el mensaje ya duplicó el mensaje.

## Criterio de aceptación

- [ ] Constraint UNIQUE aplicado vía migración de Alembic
- [ ] El mismo payload enviado dos veces crea un solo registro
- [ ] El duplicado no dispara transición de FSM ni mensaje saliente
- [ ] Ambos requests responden 200
- [ ] Test de integración que envía el mismo webhook dos veces
