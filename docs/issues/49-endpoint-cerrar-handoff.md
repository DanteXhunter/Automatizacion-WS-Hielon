## Depende de

- #47 — el estado del que se sale

## Objetivo

Consultar conversaciones e historial, y permitir que un humano devuelva al bot
una conversación específica.

## Endpoints de consulta

```
GET /admin/conversaciones?estado=EN_ASESOR_HUMANO
GET /admin/conversaciones/{id}/mensajes
```

La lista devuelve cliente, estado, última interacción y motivo del handoff. El
detalle devuelve el historial paginado y ordenado cronológicamente, incluidos
mensajes entrantes, salientes y mensajes manuales que Meta reporte.

## Endpoint

```
POST /admin/conversaciones/{id}/cerrar-handoff
```

Efecto: `estado_actual = IDLE`, limpia el contexto y opcionalmente registra
quién cerró el caso y cuándo, para tener trazabilidad de cuántos handoffs se
atendieron.

El cambio afecta únicamente al `id` solicitado. Cerrar el handoff de un cliente
no modifica el estado de ninguna otra conversación.

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
- [ ] La lista permite filtrar conversaciones que esperan asesor
- [ ] El detalle devuelve el historial paginado en orden cronológico
- [ ] Cambia el estado a `IDLE` y limpia el contexto
- [ ] Solo cambia la conversación indicada por el `id`
- [ ] Responde con el estado anterior y el nuevo
- [ ] Se envía un mensaje al cliente avisando que el bot retoma
- [ ] Endpoints visibles y probables desde Swagger (`/docs`)
