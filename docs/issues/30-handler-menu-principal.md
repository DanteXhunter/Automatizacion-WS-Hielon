## Depende de

- #19 — cliente de Meta para enviar mensajes interactivos
- #29 — handler que transiciona hacia aquí

## Objetivo

Implementar el menú principal con botones interactivos de WhatsApp.

## Reply Buttons

Estructura del mensaje interactivo:

```json
{
  "messaging_product": "whatsapp",
  "to": "521...",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": {"text": "¿En qué te ayudo?"},
    "action": {
      "buttons": [
        {"type": "reply", "reply": {"id": "hacer_pedido", "title": "Hacer pedido"}},
        {"type": "reply", "reply": {"id": "consultar", "title": "Consultar pedido"}},
        {"type": "reply", "reply": {"id": "asesor", "title": "Hablar con asesor"}}
      ]
    }
  }
}
```

**Límites de Meta:** máximo **3 botones**, título de máximo **20 caracteres**,
IDs únicos. Si necesitas más de 3 opciones hay que usar List Message (ver
issue #38). Exceder el límite devuelve 400.

## Respuesta del cliente

Llega como `type: "interactive"` con
`interactive.button_reply.id`. Ese `id` es el que se enruta, **no el título**:
el título es texto visible que puede cambiar sin romper la lógica.

## Transiciones

| Acción | Destino |
|---|---|
| `hacer_pedido` | `SELECCIONANDO_PRODUCTO` |
| `consultar` | busca el último pedido activo, muestra estado, vuelve a `MENU_PRINCIPAL` |
| `asesor` | `EN_ASESOR_HUMANO` |

## Entradas inválidas

El cliente puede escribir texto en vez de tocar un botón. Se lleva la cuenta en
`contexto.intentos_invalidos`:

- Intentos 1 y 2: repetir el menú con "Por favor elige una de las opciones"
- Intento 3: escalar a `EN_ASESOR_HUMANO`

El contador se reinicia con cada entrada válida.

## Alcance de "Consultar pedido" en este issue

En Fase 2 todavía no existe el flujo que crea pedidos (eso es Fase 3), así que
la consulta se cierra contra una tabla vacía: debe responder correctamente
"no tienes pedidos activos". La query completa se valida con datos reales al
terminar el issue #42, pero **este issue no se bloquea por eso**.

## Criterio de aceptación

- [ ] Los 3 botones se envían y se ven en el celular
- [ ] El enrutamiento usa el `id`, no el título
- [ ] "Consultar pedido" responde "no tienes pedidos activos" con la tabla vacía
- [ ] Tres entradas inválidas escalan a asesor humano
- [ ] El contador se reinicia al acertar
