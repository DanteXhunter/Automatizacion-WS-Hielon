## Depende de

- #1 — Business Manager creado (la app se vincula a él)

No depende de #2: la app se crea con el negocio sin verificar.

## Objetivo

Crear la app en developers.facebook.com que hospedará el producto WhatsApp y
expondrá las credenciales técnicas.

## Contexto

La "app" es la entidad técnica: tiene App ID, App Secret y es la que recibe los
webhooks. Se vincula al Business Manager del issue #1.

## Pasos

1. developers.facebook.com > Mis Apps > Crear app
2. Tipo: **Business** (no Consumer ni Gaming)
3. Vincular al Business Manager de Hielon

## Credenciales a resguardar

| Credencial | Dónde vive | Variable de entorno |
|---|---|---|
| App ID | Configuración > Básica | — |
| App Secret | Configuración > Básica (botón Mostrar) | `WHATSAPP_APP_SECRET` |

El **App Secret es el que firma los webhooks**. Es la credencial con la que se
valida el HMAC en el issue #18. Si se filtra, cualquiera puede inyectar
mensajes falsos al sistema.

## Criterio de aceptación

- [ ] App creada, en modo desarrollo, vinculada al Business Manager
- [ ] App ID y App Secret guardados en el gestor de contraseñas
- [ ] Confirmado que ninguna credencial quedó en el repositorio
