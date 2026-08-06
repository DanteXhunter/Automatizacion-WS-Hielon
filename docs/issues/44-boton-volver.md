## Depende de

- #27 — mapa `TRANSICIONES_ATRAS`
- #34 a #39 — los handlers donde aparece el botón

Este issue **centraliza** lo que cada handler ya resolvió por su cuenta; es
refactor, no funcionalidad nueva.

## Objetivo

Ofrecer navegación hacia atrás consistente, sin duplicar lógica en cada
handler.

## Estados con botón Volver

| Estado | Regresa a |
|---|---|
| `SELECCIONANDO_PRODUCTO` | `MENU_PRINCIPAL` |
| `CAPTURANDO_CANTIDAD` | `SELECCIONANDO_PRODUCTO` |
| `AGREGAR_MAS_O_CONTINUAR` | `CAPTURANDO_CANTIDAD` del último item |
| `CAPTURANDO_DIRECCION` | `AGREGAR_MAS_O_CONTINUAR` |
| `SELECCIONANDO_MODIFICACION` | `REVISANDO_RESUMEN` |

Sin botón Volver: `IDLE`, `MENU_PRINCIPAL`, `EN_ASESOR_HUMANO` y
`CONFIRMANDO_CANCELACION`.

## Implementación centralizada

El destino se lee del mapa `TRANSICIONES_ATRAS` de `states.py` (issue #27), no
se escribe dentro de cada handler. El dispatcher intercepta el id `volver`
antes de llamar al handler y resuelve la transición.

Ventaja: cambiar el flujo es editar un diccionario, y es imposible que un
handler quede con una transición atrás inconsistente con la documentación.

## Efectos colaterales por estado

Volver no es solo cambiar el estado, a veces hay que limpiar:

- Desde `CAPTURANDO_CANTIDAD`: borrar `producto_actual` del contexto
- Desde `AGREGAR_MAS_O_CONTINUAR`: borrar el último `pedido_item` y recargar
  su producto en el contexto (ver issue #36)
- Desde `CAPTURANDO_DIRECCION`: nada que limpiar

Estos efectos se declaran junto a la transición, no dispersos.

## Presentación

El botón ocupa uno de los 3 slots de Reply Buttons, lo que aprieta el espacio
en algunos estados. Donde ya se usa List Message, va como una fila más.

Título: `Volver` (corto, cabe en los 20 caracteres).

## Criterio de aceptación

- [ ] El botón aparece en los 5 estados listados
- [ ] La transición sale del mapa central, no de cada handler
- [ ] Volver desde `AGREGAR_MAS_O_CONTINUAR` no deja items duplicados
- [ ] Volver dos veces seguidas funciona
- [ ] Un `volver` recibido en un estado que no lo admite se ignora limpiamente
