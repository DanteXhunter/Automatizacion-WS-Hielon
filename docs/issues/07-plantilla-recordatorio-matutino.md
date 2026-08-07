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

## Costo (modelo vigente desde 1-oct-2026)

**MX$0.1565 por mensaje** enviado, categoría utility. Ya no se cobra por
conversación abierta: se cobra cada mensaje saliente, uno por uno.

Con 100 clientes de lunes a sábado: 2,600 mensajes/mes = **~MX$407/mes**, se
traduzcan en pedido o no.

Ese "o no" es el punto: un cliente que recibe 26 recordatorios y compra dos
veces al mes cuesta MX$4.07 en recordatorios. Por eso la Fase 3.5 contempla
segmentar el envío por patrón de compra en vez de mandarlo a todos a diario
(ver "Presupuesto de mensajes" en CLAUDE.md).

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
