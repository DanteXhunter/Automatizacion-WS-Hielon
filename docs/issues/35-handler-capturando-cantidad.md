## Depende de

- #23 — tablas `pedidos` y `pedido_items`
- #34 — producto seleccionado en el contexto

## Objetivo

Capturar cuántas bolsas quiere el cliente del producto seleccionado, sin
ambigüedad.

## Mensaje

```
¿Cuántas bolsas de {producto} necesitas?
```

## Validación estricta

Solo se acepta un **entero positivo**. Casos a rechazar explícitamente:

| Entrada | Acción |
|---|---|
| `10` | válido |
| `10 kg` | **rechazar** y repreguntar |
| `diez` | rechazar (v1 no interpreta lenguaje natural) |
| `0` o negativo | rechazar |
| `2.5` | rechazar |
| `999999` | rechazar por tope superior razonable |

El caso `10 kg` es el importante y está señalado explícitamente en `claude.md`:
si el cliente tiene seleccionada la bolsa de 5 kg y responde "10 kg",
**no se debe interpretar** como 2 bolsas. La ambigüedad se resuelve
preguntando, no adivinando. Un pedido mal capturado cuesta un viaje de
camioneta.

Mensaje de rechazo:

```
Necesito el número de bolsas. Por ejemplo: 10
```

## Al validar

1. Crear el pedido borrador si la conversación aún no tiene uno, y guardar su
   id en `conversaciones.pedido_borrador_id`
2. Insertar el `pedido_item` con `producto_id`, `cantidad`,
   `precio_unitario` (snapshot del catálogo) y `subtotal`
3. Limpiar `producto_actual` del contexto
4. Transicionar a `AGREGAR_MAS_O_CONTINUAR`

El snapshot de precio es lo que permite subir precios sin alterar pedidos ya
levantados.

## Tope superior

Definir un máximo por item (sugerido: 500 bolsas). Arriba de eso es más
probable un dedazo que un pedido real; se confirma con el cliente o se escala.

## Criterio de aceptación

- [ ] Solo acepta enteros positivos dentro del rango
- [ ] `10 kg` se rechaza y repregunta
- [ ] El pedido borrador se crea una sola vez por conversación
- [ ] El item guarda `precio_unitario` como snapshot
- [ ] Volver regresa a `SELECCIONANDO_PRODUCTO` sin dejar item huérfano
- [ ] Tests de todos los casos de la tabla
