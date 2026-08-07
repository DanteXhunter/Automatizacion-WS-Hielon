## Depende de

- #22 — enum de estados del pedido en el modelo

Se prueba con tests unitarios puros, sin flujo conversacional.

## Objetivo

Impedir por código que un pedido cambie a un estado que no le corresponde.

## Máquina de estados del pedido

```
borrador   -> pendiente | cancelado_cliente
pendiente  -> programado | en_ruta | cancelado_negocio | cancelado_cliente
programado -> en_ruta | cancelado_negocio | cancelado_cliente
en_ruta    -> entregado | cancelado_negocio
```

**Estados terminales:** `entregado`, `cancelado_cliente`, `cancelado_negocio`.
De ahí no se sale.

## Por qué se valida

Los cambios de estado no vienen solo de la FSM: también del panel admin
(issue #51) y en el futuro del ERP. Sin un validador central, cualquiera de
esos caminos puede dejar un pedido `entregado` de vuelta en `pendiente` y
duplicar una entrega.

## Implementación

En `src/services/pedido_service.py`:

```python
def cambiar_estado(pedido, nuevo_estado) -> None:
    # levanta TransicionInvalidaError si no está permitida
```

Nadie debe asignar `pedido.estado = X` directo. Todo pasa por esta función.
Vale la pena dejarlo escrito como comentario en el modelo.

## Casos borde

- `en_ruta -> cancelado_cliente` **no** está permitido: si el camión ya salió,
  cancelar es una decisión del negocio, no del cliente. Queda como
  `cancelado_negocio` con la nota correspondiente.
- Cambiar un pedido al estado que ya tiene: no es error, es no-op.

## Criterio de aceptación

- [ ] Función central de cambio de estado
- [ ] Transiciones inválidas levantan excepción con mensaje claro
- [ ] Los estados terminales rechazan cualquier salida
- [ ] Tests de todas las transiciones válidas
- [ ] Tests de al menos 6 inválidas, incluyendo salir de un terminal
