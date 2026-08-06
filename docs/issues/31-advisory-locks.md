## Depende de

- #28 — dispatcher donde insertar el lock (tiene el TODO marcado)

## Objetivo

Serializar el procesamiento de mensajes de un mismo cliente para evitar
condiciones de carrera.

## El problema

Un cliente manda "10" y medio segundo después "bolsas de 5". Con varios workers
de gunicorn, los dos webhooks se procesan **en paralelo**:

```
Worker A: lee estado=CAPTURANDO_CANTIDAD
Worker B: lee estado=CAPTURANDO_CANTIDAD   <- mismo estado, dato obsoleto
Worker A: escribe estado=AGREGAR_MAS
Worker B: escribe estado=AGREGAR_MAS       <- sobrescribe, item duplicado
```

Resultado: items duplicados o transiciones perdidas. Es un bug intermitente,
imposible de reproducir a mano y que solo aparece en producción.

## La solución

Un **advisory lock** de PostgreSQL es un candado por una clave arbitraria que
tú eliges, sin relación con ninguna fila. Postgres solo garantiza que dos
transacciones no lo tengan a la vez.

```sql
SELECT pg_advisory_xact_lock(hashtext(:cliente_id));
```

La variante `_xact_` se libera automáticamente al terminar la transacción, con
commit o con rollback. Es la correcta aquí: la versión sin `_xact_` exige
liberarla a mano y una excepción deja el candado colgado para siempre.

## Detalles

- El lock recibe un `bigint`, así que el UUID se convierte con `hashtext`
- Se toma **al inicio** de la transacción, antes de leer la conversación
- Clientes distintos generan claves distintas y no se bloquean entre sí
- Hay riesgo teórico de colisión de hash entre dos UUIDs: el efecto sería que
  dos clientes se serialicen innecesariamente, no un bug de datos

## Por qué no Redis

Un lock distribuido en Redis haría lo mismo, pero mete otro servicio que
desplegar, monitorear y mantener. Postgres ya está ahí y ya es la fuente de
verdad. Decisión cerrada en `claude.md`.

## Criterio de aceptación

- [ ] `src/services/locks.py` con un context manager que toma el lock
- [ ] El lock se toma antes de leer la conversación
- [ ] Se libera solo al terminar la transacción
- [ ] Test de concurrencia: dos mensajes simultáneos del mismo cliente se
      procesan en orden y no duplican items
- [ ] Test que confirme que dos clientes distintos sí corren en paralelo
