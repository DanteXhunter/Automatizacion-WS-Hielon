## Depende de

- #23 — tablas sobre las que se consulta
- #49 — mecanismo de API key

## Objetivo

Saber, sin adivinar, si el sistema está sirviendo bien.

## Métricas mínimas

| Métrica | Fuente |
|---|---|
| Mensajes recibidos por día | `COUNT(*)` sobre `mensajes` filtrado por fecha y dirección entrante |
| Pedidos confirmados por día | `COUNT(*)` sobre `pedidos` con estado distinto de `borrador` |
| Tasa de error del webhook | proporción de requests que no llegaron a procesar limpio (loguear explícitamente cada fallo) |
| Handoffs a humano por día | transiciones a `EN_ASESOR_HUMANO` |

## Implementación en v1

Sin Prometheus ni Grafana todavía, sería sobre-ingeniería para este volumen.
Basta con:

- Un endpoint `GET /admin/metricas` que corre las queries de arriba para un
  rango de fechas, protegido con la misma API key del issue #49
- O un query directo documentado en `docs/` para correr desde DBeaver

## Por qué importa desde ya

Es la única forma objetiva de detectar, por ejemplo, que el webhook empezó a
fallar silenciosamente (Meta sigue reintentando pero nada se procesa) o que
los handoffs se dispararon de golpe porque un cambio rompió un handler. Sin
esto, el primer indicio sería una llamada de Gabriel preguntando por qué no
llegó ningún pedido hoy.

## Criterio de aceptación

- [ ] Las 4 métricas son consultables sin entrar manualmente a escribir SQL
      cada vez
- [ ] El endpoint o query documentado funciona con datos reales de al menos
      un día de operación
- [ ] Protegido igual que los demás endpoints admin
