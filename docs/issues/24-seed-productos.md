## Depende de

- #23 — tabla `productos` creada

Bloqueo externo: precios reales pendientes de Gabriel. Se puede cerrar con
valores provisionales marcados como tales.

## Objetivo

Poblar el catálogo con los tres productos de hielo.

## Datos

| Nombre | peso_kg | dimensiones | precio | activo |
|---|---|---|---|---|
| Bolsa 3 kg | 3 | por confirmar | **pendiente** | true |
| Bolsa 5 kg | 5 | 30 x 60 cm | **pendiente** | true |
| Bolsa 10 kg | 10 | por confirmar | **pendiente** | true |

**Bloqueado parcialmente:** hay que confirmar precios y dimensiones reales con
Gabriel. Mientras tanto se puede sembrar con valores placeholder para
desbloquear el desarrollo, dejando marcado que no son los definitivos.

Los precios son sin IVA y sin envío, según lo definido en `claude.md`.

## Implementación

Script en `scripts/seed_productos.py`, **idempotente**: correrlo dos veces no
debe duplicar registros. Se resuelve con un upsert por nombre
(`ON CONFLICT DO NOTHING` o verificación previa).

Este script se ejecuta también en el despliegue de Fase 5, así que no puede
asumir una base vacía.

## Por qué el precio se lee de la BD y no está en el código

El precio va a cambiar. Si está hardcodeado en un handler de la FSM, cambiarlo
implica desplegar. Leyéndolo de `productos`, Gabriel lo actualiza con un
UPDATE. Además, `pedido_items.precio_unitario` guarda un snapshot al momento
del pedido, así que subir el precio no altera el histórico.

## Criterio de aceptación

- [ ] Los 3 productos existen en la tabla
- [ ] El script es idempotente, verificado corriéndolo dos veces
- [ ] Precios confirmados con Gabriel (o marcados como provisionales)
