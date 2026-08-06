## Depende de

- #24 — productos sembrados en la base
- #30 — menú que transiciona hacia aquí

## Objetivo

Permitir que el cliente elija el tipo de bolsa de hielo.

## Comportamiento

Bot envía Reply Buttons con los productos activos:

- `Bolsa 3 kg`
- `Bolsa 5 kg`
- `Bolsa 10 kg`

Los botones se construyen **leyendo la tabla `productos`** con `activo = true`,
no hardcodeados. Si Gabriel da de baja un producto con un UPDATE, desaparece
del menú sin desplegar código.

El `id` de cada botón es el UUID del producto, así el handler no tiene que
adivinar a qué registro corresponde el título.

## Restricción de los 3 botones

Hoy son exactamente 3 productos, que es el máximo de Reply Buttons. Si algún
día se agrega un cuarto, este handler debe migrar a List Message. Dejarlo
anotado como comentario en el código para que no sorprenda.

## Transiciones

| Entrada | Destino |
|---|---|
| Producto válido | `CAPTURANDO_CANTIDAD` |
| Botón Volver | `MENU_PRINCIPAL` |
| Entrada inválida | se repite la pregunta |

Al seleccionar, se guarda el `producto_id` en `conversacion.contexto` bajo una
llave tipo `producto_actual`. Todavía **no** se escribe en `pedido_items`:
el item se materializa hasta tener la cantidad (issue #35).

## Criterio de aceptación

- [ ] Los botones se generan desde la base de datos
- [ ] El `id` del botón es el UUID del producto
- [ ] La selección se guarda en el contexto JSONB
- [ ] Volver regresa a `MENU_PRINCIPAL` limpiando `producto_actual`
- [ ] Si no hay productos activos, el bot lo comunica y escala a asesor
