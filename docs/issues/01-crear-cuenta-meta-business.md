## Objetivo

Tener un Business Manager operativo a nombre de Hielon de León, que será el
contenedor de todos los activos de Meta del proyecto (app, número, plantillas).

## Contexto

Meta separa la identidad del negocio de la app técnica. El Business Manager es
la capa de arriba: ahí viven los permisos, los usuarios del sistema y el WABA
(WhatsApp Business Account). Sin esto no se puede avanzar a nada más.

Este proyecto integra **directo con Cloud API**, sin BSP (Twilio, 360dialog).
Decisión cerrada en `claude.md`.

## Pasos

1. Entrar a business.facebook.com con una cuenta de Facebook personal (Meta la
   exige como ancla; no se publica nada en ella).
2. Crear el negocio con el nombre legal de Hielon de León.
3. Agregar correo de contacto del negocio.

## Criterio de aceptación

- [ ] El negocio aparece dado de alta en business.facebook.com
- [ ] El Business ID queda anotado en el gestor de contraseñas
- [ ] Gabriel tiene acceso como administrador (no solo el desarrollador)

## Notas

Que Gabriel sea admin no es opcional: si el proyecto se entrega y el único
admin es el desarrollador, el negocio queda secuestrado técnicamente.
