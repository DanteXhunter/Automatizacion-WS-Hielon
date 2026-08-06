## Depende de

- #23 — tabla `direcciones`
- #36 — carrito cerrado que transiciona hacia aquí

## Objetivo

Determinar a dónde se entrega el pedido, aceptando dirección previa, texto
libre o ubicación de WhatsApp.

## Dos ramas según el cliente

**Con direcciones previas:**

```
¿Entregamos en la dirección de siempre?
{texto de la última dirección}
```

Botones: `Usar esta` / `Nueva dirección`

**Cliente nuevo:**

```
¿A qué dirección lo entregamos? Puedes escribirla o
compartir tu ubicación con el clip 📎 > Ubicación.
```

## Entradas aceptadas

| Tipo | Manejo |
|---|---|
| Botón "Usar esta" | se toma la dirección con `es_ultima_usada = true` |
| Texto libre | se crea una `direccion` nueva con `texto` |
| `type: "location"` | se crea con `latitud` y `longitud` |

La ubicación de WhatsApp llega así:

```json
{"type": "location", "location": {"latitude": 21.12, "longitude": -101.68,
 "name": "opcional", "address": "opcional"}}
```

Si trae `address`, se guarda también en `texto`: al repartidor le sirve más
una calle que unas coordenadas.

## Bandera es_ultima_usada

Al guardar una dirección nueva hay que poner en `false` la anterior del mismo
cliente y en `true` la nueva, **en la misma transacción**. Si quedan dos en
`true`, el botón "Usar esta" se vuelve no determinista.

## Validación mínima en v1

Sin geocodificación ni validación de zona de cobertura (eso está en el
backlog, issue #70). Solo se rechaza texto absurdamente corto, menos de 10
caracteres, con un mensaje pidiendo calle, número y colonia.

## Criterio de aceptación

- [ ] Cliente con direcciones previas ve el botón de reutilizar
- [ ] Cliente nuevo recibe la instrucción de cómo compartir ubicación
- [ ] Texto libre se guarda como dirección nueva
- [ ] Mensaje de ubicación guarda lat/lon correctamente
- [ ] Solo una dirección por cliente tiene `es_ultima_usada = true`
- [ ] Volver regresa a `AGREGAR_MAS_O_CONTINUAR`
