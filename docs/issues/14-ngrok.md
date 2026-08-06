## Depende de

- #12 — algo corriendo en localhost:8000 que exponer

## Objetivo

Exponer el servidor local a internet con HTTPS para que Meta pueda entregarle
webhooks.

## Concepto

Un webhook es Meta haciendo `POST` a una URL **tuya**. Meta no puede alcanzar
`localhost:8000` porque está dentro de tu red. ngrok abre un túnel: te da una
URL pública tipo `https://abc123.ngrok-free.app` y reenvía todo lo que llegue
ahí a tu puerto local.

Meta además exige **HTTPS con certificado válido**. ngrok lo da resuelto; por
eso no basta con abrir un puerto en el router.

## Pasos

1. `brew install ngrok`
2. Crear cuenta gratuita en ngrok.com y copiar el authtoken
3. `ngrok config add-authtoken TU_TOKEN`
4. Con uvicorn corriendo: `ngrok http 8000`

## Limitación importante

En el plan gratuito **la URL cambia cada vez que reinicias ngrok**, y hay que
reconfigurar el webhook en Meta cada vez. Se resuelve dejando ngrok corriendo
en una terminal aparte durante toda la sesión de trabajo.

Esta dependencia desaparece en Fase 5 al migrar al dominio real (issue #57).

## Criterio de aceptación

- [ ] `https://TU-URL.ngrok-free.app/health` responde 200 desde el celular con
      datos móviles (no wifi, para confirmar que sale a internet de verdad)
- [ ] Procedimiento escrito en `docs/setup-local.md`
