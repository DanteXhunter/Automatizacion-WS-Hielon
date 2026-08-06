## Depende de

- #21 — base de datos accesible

Se cierra con las clases definidas e importables; las tablas físicas se crean
en el #23.

## Objetivo

Traducir el modelo de datos de `claude.md` a clases SQLModel.

## Tablas

Una por archivo en `src/models/`: `clientes`, `direcciones`, `productos`,
`pedidos`, `pedido_items`, `conversaciones`, `mensajes`.

La definición de columnas está en `claude.md`, sección "Modelo de datos".

## Convenciones obligatorias

- **PK UUID** con `default_factory=uuid4`. Un ID autoincremental filtra cuántos
  pedidos lleva el negocio y complica la futura consolidación multi-tenant.
- **Timestamps con timezone** (`TIMESTAMPTZ`). Sin timezone, un pedido de las
  23:00 en México se guarda ambiguo y los reportes por día salen mal.
- **Enums nativos de Postgres** para `pedidos.estado` y `mensajes.direccion`.
  La base rechaza un valor inválido aunque el código tenga un bug.
- **DECIMAL para dinero**, jamás `float`. `0.1 + 0.2 != 0.3` en punto flotante
  y los totales terminan con centavos fantasma.
- **Llaves foráneas declaradas** con su índice.

## Índices necesarios

| Tabla | Columna | Motivo |
|---|---|---|
| clientes | telefono | UNIQUE, búsqueda en cada mensaje entrante |
| mensajes | whatsapp_message_id | UNIQUE, idempotencia (issue #26) |
| pedidos | numero_orden | UNIQUE |
| pedidos | cliente_id, estado | consulta de pedido activo |
| conversaciones | cliente_id | UNIQUE, una conversación por cliente |

## Criterio de aceptación

- [ ] Las 7 clases creadas, una por archivo
- [ ] Relaciones declaradas en ambos sentidos donde aplique
- [ ] Dinero en DECIMAL, fechas con timezone, PKs UUID
- [ ] `conversaciones.contexto` es JSONB
- [ ] Los índices de la tabla de arriba están declarados
