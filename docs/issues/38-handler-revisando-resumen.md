## Depende de

- #37 — dirección capturada

La acción "Confirmar" solo transiciona; la lógica de confirmación es el #42.
La nota de hora de corte es el #46. Ninguno de los dos bloquea este issue.

## Objetivo

Mostrar el pedido completo y ofrecer las cuatro acciones finales.

## Mensaje

```
Resumen de tu pedido:

- 10 x Bolsa 5 kg .......... $XXX
- 5 x Bolsa 10 kg .......... $XXX

Entrega en: {dirección}
Total: $XXX

Los precios no incluyen IVA ni envío.
```

## Problema técnico: son 4 opciones

Confirmar, Modificar, Cancelar y Hablar con asesor son cuatro, y los Reply
Buttons solo permiten tres. Hay que usar un **Interactive List Message**:

```json
{
  "type": "interactive",
  "interactive": {
    "type": "list",
    "body": {"text": "..."},
    "action": {
      "button": "Ver opciones",
      "sections": [{
        "title": "¿Qué deseas hacer?",
        "rows": [
          {"id": "confirmar", "title": "Confirmar pedido"},
          {"id": "modificar", "title": "Modificar pedido"},
          {"id": "cancelar", "title": "Cancelar pedido"},
          {"id": "asesor", "title": "Hablar con asesor"}
        ]
      }]
    }
  }
}
```

Límites: hasta 10 filas, título de 24 caracteres, descripción opcional de 72.
La respuesta llega en `interactive.list_reply.id`, no en `button_reply`.

El List Message tiene una fricción extra: el cliente debe tocar el botón y
después elegir de la lista. Peor UX que los botones, pero es la única forma de
ofrecer cuatro opciones.

## Mensaje adicional después de las 14:00

**Fuera del alcance de este issue.** El aviso de hora de corte se implementa
completo en el issue #46, que solo agrega texto al mensaje que este handler
ya construye. Este issue se cierra sin esa nota.

## Transiciones

| Entrada | Destino |
|---|---|
| `confirmar` | ver issue #42, luego `IDLE` |
| `modificar` | `SELECCIONANDO_MODIFICACION` |
| `cancelar` | `CONFIRMANDO_CANCELACION` |
| `asesor` | `EN_ASESOR_HUMANO` |

## Criterio de aceptación

- [ ] El resumen muestra items, subtotales, dirección y total
- [ ] Se usa List Message y se lee `list_reply.id`
- [ ] Las cuatro transiciones funcionan
- [ ] El total del resumen coincide con la suma de `pedido_items`
