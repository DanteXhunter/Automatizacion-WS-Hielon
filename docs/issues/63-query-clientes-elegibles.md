## Depende de

- #23 — tablas `clientes`, `conversaciones` y `pedidos`
- #61 — n8n con acceso a Postgres

## Objetivo

Seleccionar exactamente a quién sí se le debe mandar el recordatorio,
respetando consentimiento y evitando duplicar contacto.

## Query base

```sql
SELECT c.id, c.telefono, c.nombre
FROM clientes c
WHERE c.opt_in_recordatorios = true
  AND NOT EXISTS (
    SELECT 1 FROM conversaciones conv
    WHERE conv.cliente_id = c.id
      AND conv.ultima_interaccion >= CURRENT_DATE
  )
  AND NOT EXISTS (
    SELECT 1 FROM pedidos p
    WHERE p.cliente_id = c.id
      AND p.estado IN ('pendiente', 'programado', 'en_ruta')
  );
```

## Por qué cada condición

- **`opt_in_recordatorios = true`**: sin esto se viola la LFPDPPP y la
  política de mensajería de Meta. No negociable, va primero.
- **Sin conversación activa hoy**: si el cliente ya escribió hoy, mandar
  además el recordatorio es ruido, y potencialmente confunde al bot con dos
  hilos de conversación simultáneos.
- **Sin pedido en curso**: si ya tiene algo `pendiente`, `programado` o
  `en_ruta`, ya sabe que le vamos a llevar hielo; no hace falta preguntarle si
  quiere pedir.

## Ejecución desde n8n

Nodo Postgres apuntando a la misma base de producción, con credenciales de
solo lectura si es posible (un rol separado del que usa el backend, para
acotar el radio de un error de configuración en el flow).

## Criterio de aceptación

- [ ] La query corre desde el nodo Postgres de n8n sin errores
- [ ] Un cliente sin opt-in nunca aparece en el resultado
- [ ] Un cliente que ya escribió hoy no aparece
- [ ] Un cliente con pedido en curso no aparece
- [ ] Probada con datos reales o un seed representativo antes de activar el
      envío real
