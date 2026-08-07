## Depende de

- #42 — pedidos confirmados, para poder atribuir mensajes a un pedido
- #26 — guardado de mensajes ya funcionando

## Objetivo

Dejar cada mensaje saliente registrado con su categoría, su costo y el pedido
al que pertenece. Sin esto no se puede medir nada de la Fase 3.5.

## Por qué este issue vive en la Fase 3.5 y no en la 6.1

En el roadmap original la instrumentación estaba en la Fase 6.1 (dashboard),
pero la Fase 3.5 arranca midiendo el MSPC. **Medir requiere haber instrumentado
antes.** Tal como estaba, la 3.5 dependía de un issue de una fase posterior.

Se adelanta la captura del dato; los endpoints y la vista se quedan en la 6.1.

## Campos a poblar en `mensajes`

| Campo | Cuándo se llena | Valor |
|---|---|---|
| `pricing_category` | al enviar | `service` en el flujo del bot, `utility` en plantillas |
| `costo_estimado` | al enviar | la tarifa vigente de config, **snapshot** |
| `pedido_id` | al enviar | el pedido borrador en curso, o `NULL` |

## Por qué snapshot y no calcular después

Las tarifas de Meta cambian (cambiaron el 1-oct-2026 y volverán a cambiar). Si
el costo se calcula al momento de consultar, un cambio de precio **reescribe
retroactivamente el histórico** y el gasto reportado deja de cuadrar con las
facturas viejas. Guardar el valor al momento del envío lo congela.

## Por qué `pedido_id` y no solo `conversacion_id`

El MSPC es "mensajes por **pedido completado**". Una conversación puede
producir cero pedidos (el cliente preguntó y se fue) o varios. Atribuir al
pedido permite separar los mensajes que sí generaron venta de los que no.

Mensajes sin pedido asociado (recordatorio matutino, handoff, respuesta fuera
de horario) van con `NULL` y **no cuentan para el MSPC**, pero sí para el gasto
total.

## Dónde se implementa

En el wrapper de envío (`src/whatsapp/client.py`), no en cada handler. Si cada
handler tiene que acordarse de registrar el costo, tarde o temprano uno se
olvida y la métrica queda mal sin que nadie se entere.

## Criterio de aceptación

- [ ] Todo mensaje saliente queda con `pricing_category` y `costo_estimado`
- [ ] Los mensajes del flujo de pedido llevan `pedido_id`
- [ ] Recordatorios y handoffs llevan `pedido_id = NULL`
- [ ] El registro ocurre en el wrapper, no repartido por los handlers
- [ ] Migración de Alembic para los tres campos
