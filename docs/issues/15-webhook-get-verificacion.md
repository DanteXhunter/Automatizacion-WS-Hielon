## Depende de

- #13 — `settings.whatsapp_verify_token` disponible

Se cierra probando con `curl` en local; no requiere configurar nada en Meta
(eso es el #17).

## Objetivo

Implementar el handshake que Meta exige antes de empezar a mandar eventos.

## Cómo funciona

Cuando registras la URL en el panel de Meta, Meta hace un `GET` a tu endpoint
con tres query params:

```
GET /webhook/whatsapp?hub.mode=subscribe
                     &hub.verify_token=EL_QUE_TU_CONFIGURASTE
                     &hub.challenge=1158201444
```

Tu servidor debe:

1. Verificar que `hub.mode == "subscribe"`
2. Verificar que `hub.verify_token` coincide con `settings.whatsapp_verify_token`
3. Devolver **el valor de `hub.challenge` en texto plano**, con status 200

Si devuelves JSON en vez de texto plano, Meta rechaza la verificación. Es el
error más común aquí.

## Detalle de FastAPI

Los nombres tienen punto (`hub.mode`), que no es válido como nombre de
parámetro en Python. Se resuelve con alias:

```python
hub_mode: str = Query(alias="hub.mode")
```

Y la respuesta debe ser `PlainTextResponse`, no un dict.

## Criterio de aceptación

- [ ] Token correcto devuelve el challenge en texto plano con 200
- [ ] Token incorrecto devuelve 403
- [ ] Parámetros faltantes devuelven 422 o 403, nunca 500
- [ ] Probado manualmente con `curl` antes de configurarlo en Meta
