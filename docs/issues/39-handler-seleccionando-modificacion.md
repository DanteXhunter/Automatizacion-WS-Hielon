## Depende de

- #38 — resumen que transiciona hacia aquí

## Objetivo

Permitir corregir el pedido sin tener que cancelarlo y empezar de cero.

## Mensaje

```
¿Qué deseas modificar?
```

Botones: `Productos` / `Dirección` / `Volver`

## Transiciones

| Entrada | Efecto | Destino |
|---|---|---|
| `productos` | **borra todos los `pedido_items`** del borrador | `SELECCIONANDO_PRODUCTO` |
| `direccion` | no borra nada | `CAPTURANDO_DIRECCION` |
| `volver` | — | `REVISANDO_RESUMEN` |

## Alcance de v1: modificar productos vacía el carrito

Editar un item individual exige mostrar la lista, dejar elegir cuál, y decidir
si se cambia cantidad o se elimina. Son tres estados más y bastante lógica,
para un carrito que en la práctica tendrá uno o dos productos.

Decisión: vaciar y volver a capturar. Está en el backlog como issue #73.

El bot debe **avisarlo antes de borrar**, no hacerlo en silencio:

```
Vamos a capturar los productos de nuevo. Tu dirección se conserva.
```

## Consistencia

Al borrar los items hay que limpiar también `producto_actual` del contexto y
recalcular el total del pedido a cero. Un borrador con total viejo y sin items
produce un resumen incoherente si el cliente confirma rápido.

## Criterio de aceptación

- [ ] `productos` borra todos los items y avisa al cliente antes
- [ ] `direccion` conserva los items intactos
- [ ] El total se recalcula tras el borrado
- [ ] Volver regresa al resumen sin alterar nada
