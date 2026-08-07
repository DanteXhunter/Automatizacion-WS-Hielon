## Depende de

- #18 — función de validación implementada

## Objetivo

Cubrir con tests la única barrera de seguridad del webhook.

## Por qué este es el primer test del proyecto

La validación HMAC es el punto donde un bug no se nota: el sistema sigue
funcionando perfecto mientras acepta mensajes falsos. No hay síntoma visible
hasta que alguien lo explota. Por eso se prueba explícitamente en vez de
confiar en que "ya funcionó una vez".

## Casos a cubrir

| Caso | Esperado |
|---|---|
| Firma válida sobre el body correcto | pasa |
| Firma calculada con otro secreto | rechaza |
| Header `X-Hub-Signature-256` ausente | rechaza |
| Header presente pero sin el prefijo `sha256=` | rechaza |
| Body alterado en un byte, firma original | rechaza |
| Body vacío | rechaza sin excepción |
| Firma con mayúsculas y minúsculas mezcladas | decidir y documentar |

## Implementación

Test unitario puro sobre la función de `signature.py`, sin levantar el
servidor. La firma válida se genera en el propio test con `hmac`, usando un
secreto de prueba.

Adicionalmente, un test de integración con `TestClient` que confirme que el
endpoint responde 403 ante firma inválida.

## Criterio de aceptación

- [ ] `pytest tests/unit/test_signature.py` pasa con los 7 casos
- [ ] Ningún test usa el App Secret real
- [ ] Los tests corren sin conexión a internet
