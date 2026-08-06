## Depende de

- #48 — bot de Telegram para el resumen
- #64 — flow de envío al que se le agrega el manejo de errores

## Objetivo

Que un fallo puntual no tumbe toda la corrida matutina, y que Gabriel se
entere del resultado sin revisar n8n manualmente.

## Errores esperables

| Error | Causa típica | Manejo |
|---|---|---|
| 131026 | Cliente bloqueó el número o no tiene WhatsApp | Marcar `failed`, no reintentar |
| 429 / rate limit | Envíos muy rápidos | Backoff y reintento |
| 401 | Token vencido o revocado | Detener la corrida completa y alertar de inmediato, es un problema de todos los envíos, no de uno |
| Timeout de red | Intermitencia | Reintento con backoff, máximo 3 veces |

## Diseño del flow en n8n

- Nodo **Error Trigger** o rama de error en el HTTP Request, para que un fallo
  individual no detenga el **Loop Over Items**
- Cada resultado (éxito o fallo) se acumula en un arreglo en vez de perderse
- Al final del loop, un nodo que arma el resumen

## Resumen final a Telegram

```
Recordatorio matutino - 15 ago 2026
Enviados: 87
Fallidos: 3 (2 bloqueados, 1 timeout tras reintentos)
Costo estimado: $2.87 USD
```

Reutiliza el mismo bot de Telegram del issue #48, con un chat o hilo separado
para no mezclar alertas operativas de handoff con reportes de rutina.

## Caso especial: token vencido

Si el primer envío falla con 401, no tiene sentido seguir intentando los 99
restantes: todos van a fallar igual. El flow debe detectar este código
específico, cortar el loop y mandar una alerta urgente distinta al resumen de
rutina.

## Criterio de aceptación

- [ ] Un fallo individual no detiene el resto del loop
- [ ] Un 401 detiene la corrida completa y alerta de inmediato
- [ ] El resumen final llega a Telegram con conteos y costo estimado
- [ ] Probado forzando al menos un fallo simulado (número inválido)
