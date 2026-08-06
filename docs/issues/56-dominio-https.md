## Depende de

- #55 — instancia con IP elástica a la que apuntar el dominio

Bloqueo externo: comprar el dominio.

## Objetivo

Servir el backend bajo un dominio propio con HTTPS válido.

## Por qué es obligatorio, no cosmético

Meta **rechaza** webhooks sobre HTTP o con certificado autofirmado. Sin esto,
no hay forma de migrar de ngrok a producción.

## Opción recomendada: Caddy

```
api.hielondeleon.com {
    reverse_proxy backend:8000
}
```

Caddy obtiene y renueva el certificado de Let's Encrypt automáticamente, sin
configuración adicional. Para un solo desarrollador manejando esto por primera
vez, es más simple que nginx + certbot, que requiere configurar la renovación
por separado (cron o systemd timer).

## Pasos

1. Comprar o usar un dominio existente
2. Crear un registro `A` apuntando a la IP elástica de EC2
3. Agregar Caddy como servicio en el `docker-compose.yml`, en la misma red que
   `backend`
4. Verificar que el certificado se emite al primer arranque

## Verificación

```bash
curl -v https://api.hielondeleon.com/health
```

Debe responder 200 con certificado válido, verificable también con el
`openssl s_client` o simplemente revisando el candado en el navegador.

## Criterio de aceptación

- [ ] Dominio resuelve a la IP de EC2
- [ ] Certificado válido de Let's Encrypt, sin advertencias del navegador
- [ ] Renovación automática confirmada (Caddy la maneja sola)
- [ ] `/health` accesible por HTTPS desde fuera de la red de AWS
