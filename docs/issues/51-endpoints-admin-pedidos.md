## Depende de

- #43 — validador de transiciones que usa el PATCH
- #49 — mecanismo de API key ya definido

## Objetivo

Permitir que la secretaria consulte pedidos confirmados, los capture en My
Business POS 2011 y actualice su avance sin editar directamente la base.

## Endpoints

**Consulta:**

```
GET /admin/pedidos?estado=pendiente&fecha_desde=2026-08-01&fecha_hasta=2026-08-31
```

Devuelve pedidos con sus items y datos de cliente/dirección resueltos (no
solo los IDs crudos), paginado. También incluye `numero_orden`, fecha de
confirmación, total y observaciones: son los datos necesarios para capturar la
venta e imprimir el ticket desde My Business POS 2011.

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

## Operación inicial

1. El cliente confirma el pedido y el backend lo persiste con un folio único.
2. La secretaria consulta los pedidos pendientes desde `/docs` y abre el
   detalle con productos, cantidades, dirección y teléfono.
3. Captura la venta manualmente en My Business POS 2011 e imprime el ticket
   desde ese sistema.
4. Actualiza el estado del pedido mediante este API cuando corresponda.

Este flujo manual es el MVP. La posible creación automática de la venta en el
POS se investiga por separado en el issue #76 y no bloquea estos endpoints.

## Cómo se valida

La prueba de integración crea y confirma un pedido, abre una sesión de base de
datos independiente y consulta el endpoint. La respuesta debe conservar el
folio y coincidir en cliente, productos, cantidades, dirección, total y estado.
También se prueban autenticación, filtros y transiciones inválidas.

## Criterio de aceptación

- [ ] `GET /admin/pedidos` filtra por estado y rango de fecha
- [ ] La respuesta incluye los datos resueltos, no solo IDs
- [ ] El detalle contiene todos los datos necesarios para capturar la venta en
      My Business POS 2011 sin consultar tablas manualmente
- [ ] `PATCH` usa el validador de transiciones del issue #43
- [ ] Transición inválida responde 400 con mensaje claro
- [ ] Ambos protegidos con la misma API key
- [ ] Documentados y probables desde `/docs`
- [ ] Prueba de integración confirma persistencia y lectura desde una sesión
      independiente de base de datos
