## Idea de backlog

Validar un mínimo de bolsas (referencia: 20) antes de permitir confirmar el
pedido, para desalentar pedidos individuales pequeños que no son el foco del
negocio (mayoristas recurrentes y eventos, según `claude.md`).

## Pendiente de definir

- Umbral exacto con Gabriel (¿20 bolsas totales del carrito, o por producto?)
- Qué pasa si el cliente no lo alcanza: ¿se bloquea la confirmación o se
  permite con una advertencia y recargo?
- Si aplica distinto a clientes recurrentes vs. ocasionales

## Por qué no está en v1

Depende de una decisión de negocio que Gabriel no ha cerrado y que interactúa
con la política de precios. Implementarlo antes de esa definición arriesga
tener que reescribir el handler de `REVISANDO_RESUMEN` (issue #38).
