## Idea de backlog

Detectar palabras clave (por ejemplo "cancelar", "salir", "hablar con
alguien") desde **cualquier** estado de la FSM y ofrecer el paso a
`EN_ASESOR_HUMANO`, no solo desde `MENU_PRINCIPAL` y `REVISANDO_RESUMEN`
(issue #50).

## Por qué no en v1

Implementarlo bien exige que el dispatcher (issue #28) intercepte estas
palabras **antes** de pasarle el mensaje al handler del estado actual, sin
romper la lógica de validación de cada uno (por ejemplo, que "cancelar" en
`CONFIRMANDO_CANCELACION` no se confunda con la respuesta esperada de ese
mismo estado). Es una capa transversal que conviene construir con el resto de
los handlers ya estables, para no diseñarla contra un flujo que todavía puede
cambiar.

## Alcance futuro

- Lista de palabras clave de escape, configurable
- Prioridad de interpretación: primero el botón/opción esperada del estado
  actual, luego la palabra clave global
