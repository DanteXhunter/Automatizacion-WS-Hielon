## Depende de

- #23 — tabla `clientes` creada

## Objetivo

Identificar o dar de alta al cliente a partir del número que llega en el
webhook.

## Alcance

`src/services/cliente_service.py` con `get_or_create_por_telefono()`.

## Normalización del teléfono

Meta manda el `wa_id` **sin** el signo `+`: `5214771234567`. La base guarda
E.164 con `+`. Si no se normaliza, el mismo cliente se duplica según de dónde
venga el dato.

Casos que deben resolver al mismo registro:

- `5214771234567` (formato de Meta)
- `+5214771234567` (E.164)
- `+52 477 123 4567` (con espacios, si entra por el panel admin)

Números mexicanos: Meta suele incluir el `1` después del `52` para móviles.
Documentar la decisión de si se conserva o se normaliza, y ser consistente.

## Concurrencia

Dos mensajes simultáneos de un cliente nuevo pueden ejecutar el INSERT a la
vez. Sin protección, uno truena con violación de UNIQUE.

Se resuelve con `INSERT ... ON CONFLICT (telefono) DO UPDATE ... RETURNING *`,
que es atómico. El patrón "SELECT y si no existe INSERT" tiene una ventana de
carrera entre ambas operaciones.

## Nombre del cliente

El payload trae `contacts[0].profile.name`, el nombre que el cliente puso en
su perfil de WhatsApp. Se aprovecha para poblar `clientes.nombre` en el alta,
pero no se sobrescribe si ya hay un nombre capturado por un humano.

## Criterio de aceptación

- [ ] Cliente nuevo se crea con teléfono normalizado a E.164
- [ ] Cliente existente se devuelve sin duplicar
- [ ] Los tres formatos de arriba resuelven al mismo registro
- [ ] El upsert es atómico
- [ ] Tests unitarios de normalización
