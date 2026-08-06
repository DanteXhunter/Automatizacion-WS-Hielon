## Depende de

Nada. Es código puro sin dependencias de base de datos ni de Meta; se puede
hacer en cualquier momento.

## Objetivo

Formalizar los 11 estados de la conversación y el mapa de transiciones
válidas.

## Concepto

Una máquina de estados finita modela la conversación como un conjunto cerrado
de situaciones y las transiciones permitidas entre ellas. La ventaja sobre
resolverlo con `if`s: en cualquier momento sabes exactamente en qué punto está
cada cliente, y una transición no contemplada es un error explícito y no un
comportamiento raro.

Es también la razón por la que **no se usa LLM en v1**: el flujo es acotado y
un autómata determinista es más barato, más rápido y depurable.

## Alcance

`src/fsm/states.py`:

- `class EstadoConversacion(str, Enum)` con los 11 valores documentados en
  `claude.md`
- Diccionario de transiciones válidas por estado
- Diccionario de transición "atrás" por estado

Heredar de `str` permite guardar el valor directo en la columna y compararlo
sin conversiones.

## Los 11 estados

`IDLE`, `MENU_PRINCIPAL`, `SELECCIONANDO_PRODUCTO`, `CAPTURANDO_CANTIDAD`,
`AGREGAR_MAS_O_CONTINUAR`, `CAPTURANDO_DIRECCION`, `REVISANDO_RESUMEN`,
`SELECCIONANDO_MODIFICACION`, `CONFIRMANDO_CANCELACION`, `EN_ASESOR_HUMANO`,
`FUERA_DE_HORARIO`.

## Decisión sobre FUERA_DE_HORARIO

Se implementa como **condición, no como estado** (decisión cerrada en
`claude.md`). Un middleware verifica la hora antes de invocar la FSM. La razón:
como estado habría que decidir cuándo y cómo salir de él, y la conversación
perdería el punto donde iba. Como condición, el cliente retoma exactamente
donde se quedó.

Se deja en el enum por completitud documental, marcado como no utilizado.

## Estados sin transición "atrás"

`IDLE`, `MENU_PRINCIPAL`, `EN_ASESOR_HUMANO` y `CONFIRMANDO_CANCELACION`
(este último usa su propio botón "No, regresar").

## Criterio de aceptación

- [ ] Enum con los 11 estados
- [ ] Mapa de transiciones válidas completo
- [ ] Mapa de transiciones "atrás"
- [ ] Función `es_transicion_valida(origen, destino)` con tests
