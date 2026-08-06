## Idea de backlog

Permitir modificar la cantidad o eliminar un producto específico del carrito
sin vaciar todo el pedido, a diferencia del comportamiento de v1 en
`SELECCIONANDO_MODIFICACION` (issue #39), donde "Productos" borra todos los
`pedido_items` y se empieza de nuevo.

## Alcance futuro

- Nuevo estado o sub-flujo que liste los items actuales con botones para
  elegir cuál tocar
- Acciones por item: cambiar cantidad, eliminar
- Recalcular total tras cada edición puntual

## Por qué no en v1

Son varios estados adicionales y navegación más compleja, para un carrito
que en la práctica del negocio suele tener uno o dos productos. El costo de
implementarlo no se justifica todavía frente a "vaciar y recapturar".
