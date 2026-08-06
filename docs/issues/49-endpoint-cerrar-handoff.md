## Depende de

- #47 — el estado del que se sale

## Objetivo

Permitir que un humano devuelva la conversación al bot manualmente.

## Endpoint

```
POST /admin/conversaciones/{id}/cerrar-handoff
```

Efecto: `estado_actual = IDLE`, limpia el contexto y opcionalmente registra
quién cerró el caso y cuándo, para tener trazabilidad de cuántos handoffs se
atendieron.

## Protección

Este endpoint puede regresar al bot el control de una negociación a medias.
No puede quedar público. Para v1, autenticación simple por API key en un
header:

```
X-Admin-Key: {valor de settings}
```

Sin la clave correcta, 401. No es necesario OAuth completo para un solo
usuario administrador; es proporcional al riesgo actual, pero debe quedar
anotado que si el panel crece a varios usuarios, esto se reemplaza por algo
más serio.

## Respuesta

```json
{"conversacion_id": "...", "estado_anterior": "EN_ASESOR_HUMANO", "estado_actual": "IDLE"}
```

## Efecto colateral a decidir

¿El bot debe mandar un mensaje al cliente avisando que retoma ("Continuemos,
¿en qué te ayudo?") o queda en silencio hasta que el cliente vuelva a
escribir? Recomendado: mandar el aviso, para que el cliente no piense que lo
ignoraron.

## Criterio de aceptación

- [ ] El endpoint requiere la API key y rechaza sin ella con 401
- [ ] Cambia el estado a `IDLE` y limpia el contexto
- [ ] Responde con el estado anterior y el nuevo
- [ ] Se envía un mensaje al cliente avisando que el bot retoma
- [ ] Visible y probable desde Swagger (`/docs`)
