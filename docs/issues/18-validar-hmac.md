## Depende de

- #13 — `settings.whatsapp_app_secret` disponible
- #16 — endpoint POST donde insertar la validación

Se puede implementar y probar con un App Secret ficticio; no requiere el real.

## Objetivo

Rechazar cualquier request al webhook que no venga firmado por Meta.

## Contexto

Tu URL de webhook es pública. Sin validación, cualquiera que la descubra puede
mandarte un POST con un payload falso y crear pedidos fantasma, disparar
handoffs o llenar tu base de datos.

Meta firma cada request con HMAC-SHA256 usando el **App Secret** y manda el
resultado en el header:

```
X-Hub-Signature-256: sha256=a1b2c3d4...
```

## Implementación

`src/whatsapp/signature.py`:

1. Leer el header y quitarle el prefijo `sha256=`
2. Calcular `hmac.new(app_secret.encode(), body_bytes, hashlib.sha256).hexdigest()`
3. Comparar con `hmac.compare_digest(esperado, recibido)`

## Dos detalles que rompen esto en silencio

**El body debe ser los bytes exactos que llegaron.** Si haces `await request.json()`
y luego re-serializas con `json.dumps()`, el resultado difiere en espacios o en
el orden de las llaves y la firma **nunca** coincidirá. Hay que usar
`await request.body()` y validar antes de parsear.

**La comparación va con `hmac.compare_digest`, no con `==`.** El operador `==`
corta la comparación en el primer byte distinto, y ese tiempo variable permite
un ataque de timing para reconstruir la firma byte por byte. `compare_digest`
tarda lo mismo siempre.

## Criterio de aceptación

- [ ] `src/whatsapp/signature.py` con la función de verificación
- [ ] Se valida sobre el body en bytes ANTES de parsear el JSON
- [ ] La comparación usa `hmac.compare_digest`
- [ ] Firma inválida devuelve 403
- [ ] Header ausente devuelve 403
- [ ] El mensaje de error no revela cuál era la firma esperada
