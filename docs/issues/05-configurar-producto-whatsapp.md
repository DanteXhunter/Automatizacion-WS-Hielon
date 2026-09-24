## Depende de

- #4 — app creada

No depende de #2 ni #3: el número de prueba lo da Meta gratis.

## Objetivo

Agregar el producto WhatsApp a la app y dejar un número operativo capaz de
enviar mensajes.

## Pasos

1. En el panel de la app: Agregar producto > WhatsApp > Configurar
2. Se crea automáticamente un WABA (WhatsApp Business Account) y un **número
   de prueba** gratuito
3. Registrar hasta 5 números de destino de prueba (tu celular, el de Gabriel)
4. Enviar el mensaje de plantilla `hello_world` desde el panel

## Datos que se obtienen aquí

| Dato | Variable de entorno |
|---|---|
| Phone Number ID | `WHATSAPP_PHONE_NUMBER_ID` |
| WhatsApp Business Account ID | — (necesario para gestionar plantillas) |

Ojo: el Phone Number ID **no es el número telefónico**, es un identificador
numérico interno de Meta. Es el que va en la URL de la API:
`POST /v21.0/{phone_number_id}/messages`

## Criterio de aceptación

- [ ] Producto WhatsApp agregado a la app
- [ ] Números de prueba registrados
- [ ] Mensaje `hello_world` recibido en un celular real
- [ ] Phone Number ID y WABA ID documentados

## Nota

Con esto ya se puede desarrollar todo, sin esperar la verificación del negocio
(issue #2) ni el número dedicado (issue #3). Es el desbloqueo de la Fase 1.

Este issue usa exclusivamente el número de prueba de Meta. No autoriza registrar
ni migrar el número comercial de Hielon. El alta definitiva se realiza en el
issue #3 únicamente después de comprobar que Coexistence está disponible.
