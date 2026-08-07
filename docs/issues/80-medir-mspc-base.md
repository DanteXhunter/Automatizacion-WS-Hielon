## Depende de

- #79 — instrumentación de costos
- #44 — flujo de pedido completo, incluido el botón Volver

## Objetivo

Tener el número real de mensajes salientes por pedido completado **antes** de
optimizar nada. Es la línea base contra la que se mide todo lo demás.

## Por qué medir antes de optimizar

El cálculo teórico del CLAUDE.md dice 7 mensajes en el camino feliz. El número
real va a ser mayor: incluye errores de captura, botones "Volver", entradas
inválidas y clientes que abandonan a medias.

Optimizar sin la línea base deja sin forma de saber si un cambio ayudó. Y peor:
lleva a optimizar el camino feliz cuando el gasto real puede estar en los
caminos de error.

## Query base

```sql
SELECT p.id, p.numero_orden, COUNT(m.id) AS mensajes, SUM(m.costo_estimado) AS costo
FROM pedidos p
JOIN mensajes m ON m.pedido_id = p.id AND m.direccion = 'saliente'
WHERE p.estado NOT IN ('borrador', 'cancelado_cliente')
GROUP BY p.id, p.numero_orden;
```

## Qué reportar

- **MSPC promedio** y **mediana** (la mediana importa: un pedido patológico de
  30 mensajes distorsiona el promedio)
- **Distribución**: cuántos pedidos en 4-6 mensajes, cuántos en 7-10, cuántos
  arriba de 10
- **Mensajes desperdiciados**: los de conversaciones que nunca produjeron
  pedido. Es gasto puro.
- **Costo por pedido** en MXN

## Con qué datos

Con tráfico real si ya lo hay. Si no, con un guion de pruebas que recorra los
caminos típicos: pedido limpio, pedido con un "Volver", pedido con dos entradas
inválidas, conversación abandonada. Documentar cuál se usó.

## Criterio de aceptación

- [ ] MSPC promedio y mediana calculados y anotados en `docs/mspc-baseline.md`
- [ ] Distribución documentada, no solo el promedio
- [ ] Contado el gasto de conversaciones sin pedido
- [ ] La medición es reproducible: la query queda guardada
