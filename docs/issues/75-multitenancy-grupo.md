## Idea de backlog

Agregar la dimensión de negocio al modelo de datos para que el mismo sistema
sirva a Cerpomex (carne) y Fruvec (fruta y verdura), además de Hielon.

## Alcance futuro

- Columna `negocio_id` (o tabla `negocios`) en `clientes`, `productos`,
  `pedidos` y todo lo que hoy asume un solo negocio implícito
- Aislamiento de datos entre negocios en cada query
- Cada negocio con su propio número de WhatsApp, catálogo, horario y
  plantillas HSM
- Decidir si es una sola instancia del backend sirviendo a los tres, o
  instancias separadas compartiendo el mismo código

## Por qué no en v1

`claude.md` es explícito en que el diseño debe **pensarse** con esto en mente
(de ahí los UUID en vez de IDs autoincrementales, por ejemplo), pero
implementarlo ahora sin un segundo negocio real operando sería diseñar a
ciegas. Se aborda cuando Cerpomex o Fruvec estén listos para su propia
automatización.
