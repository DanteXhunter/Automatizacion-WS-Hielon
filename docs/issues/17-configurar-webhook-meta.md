## Depende de

- #5 — número de prueba de Meta disponible
- #14 — ngrok exponiendo el localhost
- #15 — endpoint GET de verificación
- #16 — endpoint POST que recibe eventos

Este es el primer issue de Fase 1 que **sí** requiere Fase 0 avanzada.

## Objetivo

Conectar el webhook en el panel de Meta y confirmar el circuito completo con un
mensaje enviado desde un celular real.

## Pasos

1. Con uvicorn y ngrok corriendo, copiar la URL pública de ngrok
2. Panel de la app > WhatsApp > Configuración > Webhooks > Editar
3. Callback URL: `https://TU-URL.ngrok-free.app/webhook/whatsapp`
4. Verify Token: el mismo valor de `WHATSAPP_VERIFY_TOKEN` en tu `.env`
5. Guardar. Meta dispara el `GET` del issue #15 en ese momento.
6. Suscribirse al campo **`messages`** (sin esto no llega nada, aunque la
   verificación haya pasado)

## Prueba

Enviar un WhatsApp desde uno de los números de prueba registrados hacia el
número de prueba de Meta. El payload debe aparecer en los logs de uvicorn en
menos de 2 segundos.

La primera validación se hace con los activos de prueba. No se modifica el
número comercial ni su aplicación de WhatsApp Business para cerrar este issue.
La prueba con el número definitivo ocurre después de validar Coexistence.

## Criterio de aceptación

- [ ] Verificación del webhook exitosa en el panel
- [ ] Campo `messages` suscrito
- [ ] Mensaje real recibido y visible en los logs locales
- [ ] El JSON recibido queda pegado en el comentario de cierre del issue, como
      referencia para construir el parser

## Si no llega nada

- Confirmar que la suscripción al campo `messages` quedó activa
- Confirmar que el número emisor está en la lista de números de prueba
- Revisar la interfaz de ngrok en `http://localhost:4040`, que muestra cada
  request entrante y su respuesta
