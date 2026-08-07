## Depende de

- #4 — app creada
- #5 — WABA existente (se asigna como activo al System User)

## Objetivo

Obtener un token de acceso que no expire, para que el backend pueda llamar a
Cloud API en producción.

## Contexto

El token que Meta muestra por defecto en el panel de WhatsApp **expira en 24
horas**. Sirve para probar a mano, no para un servicio corriendo. El token
permanente se genera a través de un **System User**: una cuenta de servicio
que pertenece al negocio y no a una persona.

## Pasos

1. Business Settings > Usuarios > Usuarios del sistema > Agregar
2. Rol: Administrador
3. Asignar activos: la app (issue #4) y el WABA (issue #5), con permiso de
   control total
4. Generar nuevo token seleccionando la app y estos permisos:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
5. Caducidad: **Nunca**

## Criterio de aceptación

- [ ] System User creado con los activos asignados
- [ ] Token generado con los dos permisos y sin caducidad
- [ ] Token guardado en gestor de contraseñas, cargado en `.env` como
      `WHATSAPP_ACCESS_TOKEN`
- [ ] Verificado con una llamada de prueba a la Graph API
- [ ] Confirmado que `.env` está en `.gitignore`

## Seguridad

Este token permite enviar mensajes a nombre del negocio y cobra a la cuenta de
Meta. Se muestra **una sola vez** al generarlo. Si se filtra, hay que revocarlo
desde el System User y generar uno nuevo.

Nunca debe aparecer en logs, en capturas de pantalla ni en el repositorio.
