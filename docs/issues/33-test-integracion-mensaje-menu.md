## Depende de

- #26 — idempotencia (uno de los casos que se prueba)
- #30 — el flujo completo hasta el menú

## Objetivo

Validar el camino completo de un mensaje entrante, con Meta simulada.

## Escenario

```
POST /webhook/whatsapp con firma HMAC válida y payload de un cliente nuevo
  =>
  - el cliente se crea en la base
  - el mensaje entrante se guarda
  - se hace una llamada saliente a Meta con el menú
  - la conversación queda en MENU_PRINCIPAL
  - la respuesta HTTP es 200
```

## Cómo mockear Meta

Con `respx`, que intercepta las llamadas de httpx, o con un monkeypatch del
cliente de WhatsApp. Los tests **no deben tocar la red real**: mandarían
mensajes de verdad y dependerían del token.

Lo que sí se verifica del mock: que se llamó, a qué número, y que el cuerpo
lleva los 3 botones esperados.

## Base de datos de prueba

Base separada (`hielon_test`) con las migraciones aplicadas, y cada test
dentro de una transacción que se revierte al terminar. Así los tests no se
contaminan entre sí ni dependen del orden de ejecución.

## Criterio de aceptación

- [ ] `pytest tests/integration/test_webhook.py` pasa
- [ ] El test no hace ninguna llamada de red real
- [ ] Corre contra `hielon_test`, nunca contra `hielon_dev`
- [ ] Cada test deja la base como la encontró
- [ ] Incluye el caso de idempotencia: mismo payload dos veces, un solo efecto
