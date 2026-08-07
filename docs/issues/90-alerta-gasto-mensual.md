## Depende de

- #86 — cálculo de gasto
- #48 — mecanismo de notificación por WhatsApp a Gabriel

## Objetivo

Que Gabriel se entere de que el gasto se disparó **antes** de que llegue la
factura de Meta.

## Cuándo se dispara

Un chequeo diario (n8n, mismo cron de la Fase 6) evalúa:

| Condición | Alerta |
|---|---|
| Gasto acumulado > `ALERTA_GASTO_MENSUAL_MXN` | inmediata |
| Proyección a fin de mes > umbral | preventiva, una sola vez |
| Gasto de un día > 3x el promedio de los 7 días previos | anomalía |

La tercera es la más importante: **detecta un bug en horas, no a fin de mes.**
Un loop en la FSM que reenvía el menú puede quemar cientos de pesos en una
noche sin que nadie lo note.

## Plantilla `alerta_gasto`

```
Alerta de gasto WhatsApp.
Periodo: {{1}}
Gasto acumulado: MX${{2}}
Proyeccion a fin de mes: MX${{3}}
Motivo: {{4}}
```

Categoría **utility**. Cuidado con el copy: nada que Meta pueda leer como
promocional, o reclasifica la plantilla a marketing.

## Anti-spam de la propia alerta

**Máximo una alerta por tipo por día.** Una alerta que se manda 40 veces cuesta
dinero y entrena a Gabriel a ignorarla, que es peor que no tenerla. Guardar en
base la última vez que se envió cada tipo.

## La ironía, documentada a propósito

Este sistema **gasta mensajes para avisar que se están gastando mensajes**. A
MX$0.1565 por alerta y con el tope de una diaria, son MX$4.07/mes en el peor
caso. Vale la pena, pero queda escrito para que nadie se sorprenda al verlo en
el desglose.

## Criterio de aceptación

- [ ] Chequeo diario corriendo
- [ ] Las tres condiciones implementadas
- [ ] Plantilla `alerta_gasto` aprobada en categoría utility
- [ ] Máximo una alerta por tipo por día, verificado
- [ ] La alerta se registra en `mensajes` como cualquier otro saliente
- [ ] Probado forzando el umbral a un valor bajo
