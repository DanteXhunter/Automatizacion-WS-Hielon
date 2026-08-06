## Depende de

- #17 — webhook ya funcionando (aquí solo cambia la URL)
- #54 — stack corriendo en el servidor
- #56 — dominio con HTTPS válido

## Objetivo

Cortar la dependencia de ngrok y de la laptop del desarrollador para el
webhook.

## Pasos

1. Panel de Meta > WhatsApp > Configuración > Webhooks
2. Cambiar Callback URL a `https://api.hielondeleon.com/webhook/whatsapp`
3. Verify Token: el mismo de siempre, ya debe estar en el `.env` de EC2
4. Guardar; Meta repite el handshake `GET` del issue #15 contra la nueva URL
5. Confirmar la suscripción al campo `messages` sigue activa

## Prueba de extremo a extremo

Enviar un mensaje real desde un celular hacia el número de producción (si ya
se completó la Fase 0 con el número dedicado) o hacia el número de prueba, y
confirmar que:

- Llega al backend en EC2
- Se guarda en Postgres de producción
- La respuesta del bot llega al celular

## Qué hacer con ngrok después de esto

Se puede seguir usando en local para pruebas de features nuevas antes de
subirlas, pero **el webhook de producción registrado en Meta ya no depende de
que tu laptop esté prendida**. Es el punto de no retorno de "esto ya es un
servicio real".

## Criterio de aceptación

- [ ] Callback URL apuntando al dominio de producción
- [ ] Verificación exitosa contra el nuevo endpoint
- [ ] Mensaje real completa el ciclo completo en producción
- [ ] ngrok deja de ser necesario para que el sistema funcione
