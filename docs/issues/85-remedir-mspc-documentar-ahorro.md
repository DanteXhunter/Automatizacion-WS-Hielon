## Depende de

- #81, #82, #83, #84 — todas las optimizaciones aplicadas

## Objetivo

Cerrar la Fase 3.5 con el número final y decidir si alguna optimización debe
revertirse.

## Qué se compara

Contra la línea base de `docs/mspc-baseline.md` (issue #80):

| Métrica | Base | Ahora | Δ |
|---|---|---|---|
| MSPC promedio | | | |
| MSPC mediana | | | |
| MSPC del cliente recurrente | | | |
| Costo por pedido (MXN) | | | |
| Mensajes sin pedido asociado | | | |
| Tasa de abandono a mitad de flujo | | | |

## La métrica que puede obligar a revertir

**Tasa de abandono.** Si el MSPC bajó de 7 a 4 pero el abandono subió del 5% al
15%, la optimización salió cara: cada pedido perdido vale mucho más que los
tres mensajes que se ahorraron.

Un pedido promedio son cientos de pesos. Tres mensajes son MX$0.47. La
aritmética no está ni cerca de ser pareja.

## Meta de la fase

MSPC promedio **≤ 5** para cliente nuevo y **≤ 3** para cliente recurrente, sin
que suba el abandono.

## Salida

Actualizar `docs/mspc-baseline.md` con los resultados y, si algo se revirtió,
dejar escrito qué y por qué. Ese documento es la evidencia de que la
optimización se hizo con datos y no a ojo.

## Criterio de aceptación

- [ ] Tabla comparativa completa, con base y resultado
- [ ] Tasa de abandono medida antes y después
- [ ] Cualquier optimización que empeore el abandono, revertida y documentada
- [ ] `docs/mspc-baseline.md` actualizado
- [ ] Sección 2.1 del CLAUDE.md actualizada con el MSPC real
