## Depende de

- #55 — servicio desplegado en Railway

Sin bloqueo externo: **ya no hay que comprar dominio en v1.**

## Objetivo

Tener el backend accesible por HTTPS con certificado válido, que es el
requisito de Meta para el webhook.

## Por qué es obligatorio, no cosmético

Meta **rechaza** webhooks sobre HTTP o con certificado autofirmado. Sin HTTPS
válido no hay forma de migrar de ngrok a producción.

## Por qué ya no hay Caddy ni Let's Encrypt (decisión revisada 6-ago-2026)

Este issue originalmente compraba un dominio, creaba un registro `A` hacia la
IP elástica de EC2 y levantaba Caddy como reverse proxy para emitir el
certificado. Con Railway nada de eso existe: **la plataforma emite y renueva el
TLS del subdominio automáticamente.**

Se pasa de un issue de medio día con tres piezas nuevas (DNS, reverse proxy,
ACME) a apretar un botón.

## Pasos

1. Railway > el servicio del backend > **Settings > Networking**
2. **Generate Domain** — entrega algo como
   `automatizacion-ws-hielon-production.up.railway.app`
3. Anotar la URL; es la que se registra en Meta en el issue #57

## Verificación

```bash
curl -i https://<subdominio>.up.railway.app/health
```

Debe responder `200` con certificado válido. Si `curl` no se queja del
certificado, Meta tampoco lo hará.

## Por qué no se compra dominio propio en v1

El webhook de Meta solo necesita un endpoint HTTPS válido. No le importa si la
URL es bonita, si está indexada o si tiene sitio web. Un dominio propio son
~USD $12/año y una tarea de DNS a cambio de estética que ningún cliente ve:
**los clientes de Hielon nunca ven esta URL**, solo hablan por WhatsApp.

Revisar cuando: el grupo empresarial ya tenga dominio registrado, o el
proyecto pase a producción definitiva y se quiera desacoplar del proveedor.
Migrar después es agregar un CNAME, no rehacer nada.

## Criterio de aceptación

- [ ] Subdominio generado y anotado
- [ ] `/health` responde 200 por HTTPS desde fuera de la red local
- [ ] Sin advertencias de certificado en navegador ni en `curl`
- [ ] Confirmado que la URL sobrevive a un redeploy (no cambia como ngrok)
