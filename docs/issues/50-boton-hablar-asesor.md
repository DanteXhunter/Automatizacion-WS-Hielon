## Depende de

- #30 y #38 — los dos menús donde se agrega la opción
- #47 — estado destino
- #48 — notificación que se dispara

## Objetivo

Dar salida hacia un humano en los dos puntos de mayor fricción del flujo.

## Ubicación

- `MENU_PRINCIPAL` (issue #30): tercer botón del menú
- `REVISANDO_RESUMEN` (issue #38): cuarta fila de la lista

En v1, estos son los **únicos** dos puntos con esta salida explícita. Un
escape hatch disponible desde cualquier estado está en el backlog (issue #72);
por ahora se acotó a donde más pasa: alguien que quiere regatear el precio
(típicamente en el resumen) o que de entrada no quiere usar el flujo
automatizado (en el menú).

## Comportamiento al presionar

1. Transicionar a `EN_ASESOR_HUMANO`
2. Disparar la notificación de WhatsApp a Gabriel (issue #48) con motivo
   `"escape_hatch"` y el estado desde el que se activó
3. Responder al cliente:

```
Te comunico con un asesor, en un momento te atienden.
```

## Diferencia con el escalamiento automático

Este es voluntario (el cliente lo pide); el del issue #30 es automático (tres
entradas inválidas). Ambos llegan al mismo estado, pero el motivo que se
reporta en la notificación es distinto para que Gabriel sepa si el cliente pidió
ayuda o si el bot se atoró solo.

## Si viene desde REVISANDO_RESUMEN con un borrador activo

El pedido borrador **no se cancela ni se confirma**. Queda tal cual, para que
el asesor humano decida con el cliente si continúa o se ajusta.

## Criterio de aceptación

- [ ] Disponible en los dos estados mencionados
- [ ] Dispara notificación con el motivo correcto en cada caso
- [ ] El borrador de `REVISANDO_RESUMEN` no se toca al escalar
- [ ] El cliente recibe confirmación de que será atendido por un humano
