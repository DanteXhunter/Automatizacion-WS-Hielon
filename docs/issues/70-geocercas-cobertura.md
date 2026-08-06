## Idea de backlog

Validar que la ubicación recibida en `CAPTURANDO_DIRECCION` (issue #37) caiga
dentro del área de reparto, usando un polígono de cobertura (geocerca) en vez
de aceptar cualquier coordenada.

## Alcance futuro

- Definir el polígono de cobertura con Gabriel
- Verificación con una librería de geometría (Shapely) o una consulta
  espacial en Postgres con PostGIS
- Si cae fuera: no rechazar de golpe, escalar a `EN_ASESOR_HUMANO` para que un
  humano decida si de todos modos se puede entregar

## Por qué no en v1

Requiere PostGIS o una librería adicional, y sobre todo requiere que el
negocio defina su zona real de reparto, que hoy no está formalizada.
