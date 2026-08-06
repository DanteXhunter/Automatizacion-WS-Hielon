## Depende de

- #35 — items en el carrito que mostrar

## Objetivo

Permitir varios productos en un mismo pedido.

## Mensaje

Resumen parcial del carrito más los botones:

```
Tu pedido va así:
- 10 x Bolsa 5 kg .... $XXX
- 5 x Bolsa 10 kg .... $XXX
Total parcial: $XXX

¿Deseas agregar otro producto?
```

Botones: `Agregar otro` / `Continuar`

El total se recalcula sumando los `subtotal` de los items, no se acumula en
una variable del contexto. Recalcular desde la fuente de verdad evita que un
"volver" deje el total desfasado.

## Transiciones

| Entrada | Destino |
|---|---|
| `agregar_otro` | `SELECCIONANDO_PRODUCTO` |
| `continuar` | `CAPTURANDO_DIRECCION` |
| Botón Volver | `CAPTURANDO_CANTIDAD` del último item |

## El caso "Volver" es especial

Regresar aquí significa corregir la cantidad recién capturada. Implica
**borrar el último `pedido_item`** y volver a preguntar la cantidad con ese
mismo producto cargado en el contexto. Si no se borra, al re-capturar se
duplica el item.

## Producto repetido

Si el cliente elige un producto que ya está en el carrito, en v1 se agrega
como un item separado. Consolidarlos suena mejor pero complica el "volver";
queda documentado como comportamiento conocido.

## Criterio de aceptación

- [ ] El resumen parcial muestra todos los items con subtotal y total
- [ ] El total se recalcula desde `pedido_items`
- [ ] Volver borra el último item y repregunta su cantidad
- [ ] Un carrito con 3 productos distintos se muestra correcto
