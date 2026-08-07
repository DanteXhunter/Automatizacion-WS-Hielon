## Depende de

- #87 — métrica MSPC funcionando

## Objetivo

Saber qué clientes consumen mensajes sin comprar, para poder actuar.

## Endpoint

```
GET /admin/costos/clientes?desde=2026-10-01&orden=costo_sin_pedido
```

```json
[
  {
    "cliente_id": "...", "nombre": "Restaurante X", "telefono": "+52...",
    "mensajes_recibidos": 156, "costo_mxn": 24.41,
    "pedidos": 0, "recordatorios_recibidos": 26,
    "costo_por_pedido_mxn": null
  }
]
```

## Para qué sirve de verdad

Tres decisiones concretas salen de aquí:

1. **A quién dejar de mandarle el recordatorio matutino.** Un cliente con 26
   recordatorios y cero pedidos en el mes cuesta MX$4.07. Con 50 clientes así,
   son ~MX$200/mes tirados.
2. **Quién necesita atención humana.** Un cliente con muchos mensajes y pocos
   pedidos puede estar atorándose en el flujo, no desinteresado. Ese caso es un
   problema de diseño de la FSM, no de segmentación.
3. **Quién es rentable.** Costo de mensajería contra valor de sus pedidos.

## Cuidado con la conclusión fácil

Que un cliente no compre este mes no significa que haya que darlo de baja. Un
mayorista estacional puede pedir fuerte en diciembre y nada en octubre.
**Comparar contra su propio histórico, no contra el promedio de todos.**

## Relación con la segmentación de recordatorios

Este endpoint es el insumo de la estrategia 5 del CLAUDE.md ("recordatorio
matutino segmentado, no masivo"). Sin este dato, la segmentación sería a ojo.

## Criterio de aceptación

- [ ] Costo por cliente en el periodo, ordenable
- [ ] Distingue mensajes del flujo de pedido de recordatorios
- [ ] Identifica clientes con recordatorios y cero pedidos
- [ ] Compara contra el histórico del propio cliente, no solo el mes
- [ ] Mismo esquema de API key que #86
