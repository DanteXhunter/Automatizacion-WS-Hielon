## Idea de backlog

Permitir que el cliente elija una fecha de entrega futura, usando el campo
`pedidos.fecha_entrega` y el estado `programado` que ya existen en el modelo
de datos de `claude.md` pero no se usan activamente en v1.

## Alcance futuro

- Nuevo paso en el flujo para capturar la fecha deseada
- Validación de fechas razonables (no en el pasado, no más allá de X días)
- Vista para el negocio de "pedidos programados para mañana" que se conecte
  con la sugerencia del issue #46, cerrando ese ciclo de verdad en vez de solo
  advertir
