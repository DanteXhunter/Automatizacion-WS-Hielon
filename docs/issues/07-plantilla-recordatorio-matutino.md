## Depende de

- #5 — WABA existente (las plantillas se registran contra él)

## Objetivo

Registrar y conseguir la aprobación de la plantilla HSM que envía el cron de
las 6:00 AM.

## Contexto

Fuera de la ventana de sesión de 24 horas, el negocio **solo puede iniciar
conversación con plantillas pre-aprobadas por Meta**. El recordatorio matutino
siempre cae fuera de esa ventana, así que obligatoriamente es plantilla.

La aprobación tarda **de 1 hora a 3 días**. Cualquier cambio posterior al
texto exige volver a aprobar. Definir bien el copy desde ahora.

## Definición

- **Nombre:** `recordatorio_matutino`
- **Categoría:** UTILITY (no MARKETING; utility es más barata y se aprueba
  más fácil porque da seguimiento a una relación comercial existente)
- **Idioma:** `es_MX`

**Cuerpo:**

```
Buenos días {{1}}. ¿Deseas hacer un pedido de hielo hoy? Responde a este
mensaje para comenzar.
```

- `{{1}}` = nombre del cliente

## Costo

Conversación utility iniciada por el negocio: aproximadamente **0.033 USD**.
Con 100 clientes diarios de lunes a sábado son unos 85 USD al mes. Vale la
pena tenerlo presente antes de activar el envío masivo.

## Criterio de aceptación

- [ ] Plantilla creada en el Template Manager
- [ ] Estatus **APPROVED**
- [ ] Nombre exacto, idioma y orden de variables documentados en
      `docs/plantillas-hsm.md`
- [ ] Probada manualmente desde el panel con una variable real

## Si es rechazada

Los motivos típicos son texto promocional en una plantilla utility, variables
al inicio o al final del cuerpo, o formato incorrecto. Se corrige y se
reenvía; no penaliza la cuenta.
