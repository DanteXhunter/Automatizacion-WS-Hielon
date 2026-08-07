## Depende de

- #43 — validador de transiciones que usa el PATCH
- #49 — mecanismo de API key ya definido

## Objetivo

Operar el negocio sin necesitar DBeaver abierto todo el día.

## Endpoints

**Consulta:**

```
GET /admin/pedidos?estado=pendiente&fecha_desde=2026-08-01&fecha_hasta=2026-08-31
```

Devuelve pedidos con sus items y datos de cliente/dirección resueltos (no
solo los IDs crudos), paginado.

**Avance de estado:**

```
PATCH /admin/pedidos/{id}/estado
{"nuevo_estado": "en_ruta"}
```

Usa el validador central del issue #43: si la transición es inválida, 400
con el motivo. No es un `UPDATE` directo a la columna.

## Protección

Misma API key del issue #49. Mismo criterio: proporcional a un solo
administrador en v1, revisar si el equipo crece.

## Por qué esto y no solo Swagger + DBeaver

`claude.md` dice explícitamente que v1 no lleva panel React y que la
visualización es vía Swagger. Este endpoint es justamente lo que hace que
Swagger sea suficiente: sin él, avanzar un pedido de `pendiente` a `en_ruta`
requeriría un UPDATE manual en la base, saltándose el validador de
transiciones y arriesgando un estado inconsistente.

## Criterio de aceptación

- [ ] `GET /admin/pedidos` filtra por estado y rango de fecha
- [ ] La respuesta incluye los datos resueltos, no solo IDs
- [ ] `PATCH` usa el validador de transiciones del issue #43
- [ ] Transición inválida responde 400 con mensaje claro
- [ ] Ambos protegidos con la misma API key
- [ ] Documentados y probables desde `/docs`
