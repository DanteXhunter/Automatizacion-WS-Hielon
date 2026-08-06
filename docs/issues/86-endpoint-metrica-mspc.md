## Depende de

- #78 — mensajes con `pedido_id`
- #85 — patrón de endpoint admin ya establecido

## Objetivo

Exponer el MSPC como métrica consultable, no como una query que alguien corre a
mano cada vez.

## Endpoint

```
GET /admin/metricas/mspc?desde=2026-10-01&hasta=2026-10-31
```

```json
{
  "pedidos_completados": 812,
  "mspc_promedio": 4.7,
  "mspc_mediana": 4.0,
  "mspc_p90": 9.0,
  "distribucion": {"1-3": 190, "4-6": 480, "7-10": 118, "11+": 24},
  "costo_promedio_por_pedido_mxn": 0.74,
  "mensajes_sin_pedido": {"cantidad": 1830, "costo_mxn": 286.40}
}
```

## Por qué mediana y p90, no solo promedio

Un pedido patológico de 40 mensajes (cliente que se atoró y volvió cinco veces)
mueve el promedio y esconde que el 90% de los pedidos van bien. **La mediana
dice cómo va el caso típico; el p90 dice qué tan malo es el peor caso normal.**

Optimizar mirando solo el promedio lleva a perseguir outliers en vez de mejorar
el flujo real.

## `mensajes_sin_pedido`

Los que tienen `pedido_id = NULL`: recordatorios, handoffs, conversaciones que
no compraron. **Es gasto que no produjo venta** y suele ser el número más
incómodo del reporte. Va aparte para que no diluya el MSPC.

## Qué pedidos cuentan

Solo `pendiente`, `programado`, `en_ruta` y `entregado`. Los `borrador` y
`cancelado_*` no son pedidos completados, pero sus mensajes sí deben aparecer
en `mensajes_sin_pedido`: se gastaron igual.

## Criterio de aceptación

- [ ] Promedio, mediana, p90 y distribución
- [ ] Mensajes sin pedido reportados aparte, con su costo
- [ ] Solo pedidos completados cuentan para el MSPC
- [ ] Mismo esquema de API key que #85
