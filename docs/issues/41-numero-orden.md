## Depende de

- #23 — tabla `pedidos` con la columna `numero_orden`

Es una pieza aislada: se prueba generando folios sin necesidad del flujo
conversacional.

## Objetivo

Generar un folio legible y único por pedido confirmado.

## Formato

```
2026-0142
```

Año más consecutivo de 4 dígitos con ceros a la izquierda. El contador
reinicia cada año.

Se usa un folio legible además del UUID porque un cliente no puede dictar por
teléfono `a3f8b2c1-...`, y "mi pedido 2026-0142" sí funciona en una llamada.

## Cómo NO generarlo

```python
numero = db.query(Pedido).count() + 1   # MAL
```

Dos confirmaciones simultáneas leen el mismo count y generan el mismo folio.
Uno de los dos truena contra el constraint UNIQUE, o peor, si no hay
constraint, quedan dos pedidos con el mismo número.

Tampoco sirve `MAX(numero_orden) + 1`: mismo problema de carrera.

## Cómo sí

**Opción A (recomendada):** secuencia nativa de Postgres.

```sql
CREATE SEQUENCE pedidos_folio_seq;
SELECT nextval('pedidos_folio_seq');
```

`nextval` es atómico y no bloquea. Para el reinicio anual, un `setval` el 1 de
enero, o incluir el año en el nombre de la secuencia.

**Opción B:** tabla contador con `SELECT ... FOR UPDATE`. Funciona pero
serializa todas las confirmaciones.

Nota: las secuencias no reciclan números en un rollback, así que puede haber
huecos en el folio. Es aceptable: el folio identifica, no cuenta.

## Criterio de aceptación

- [ ] Formato `AAAA-NNNN` con ceros a la izquierda
- [ ] Constraint UNIQUE en `pedidos.numero_orden`
- [ ] Generación atómica, sin COUNT ni MAX
- [ ] Documentada la estrategia de reinicio anual
- [ ] Test de concurrencia: 50 confirmaciones simultáneas, 50 folios distintos
