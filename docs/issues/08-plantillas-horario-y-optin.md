## Objetivo

Registrar las dos plantillas HSM de apoyo del sistema.

## Plantilla 1: `fuera_de_horario`

- **Categoría:** UTILITY
- **Idioma:** `es_MX`

```
Gracias por escribirnos. Nuestro horario de atención es de lunes a sábado de
7:00 a 17:00. Te atenderemos en cuanto abramos.
```

Sin variables. Se usa cuando el cliente escribe fuera de horario y no hay
ventana de sesión abierta. Si la ventana de 24 h sí está abierta, se puede
mandar texto libre y esta plantilla no es necesaria.

## Plantilla 2: `bienvenida_opt_in`

- **Categoría:** UTILITY
- **Idioma:** `es_MX`

```
Hola {{1}}, soy el asistente de pedidos de Hielon de León. ¿Quieres que te
enviemos un recordatorio cada mañana para tu pedido de hielo? Consulta nuestro
aviso de privacidad en {{2}}
```

Botones de respuesta rápida: `Sí, quiero` / `No, gracias`

## Por qué el opt-in es obligatorio

La LFPDPPP exige consentimiento explícito para comunicación proactiva, y la
política de Meta sanciona el envío no solicitado con bajada de calidad del
número y eventual bloqueo. La respuesta a esta plantilla es la que pone
`clientes.opt_in_recordatorios` en TRUE.

## Depende de

**#9 (aviso de privacidad).** La plantilla `bienvenida_opt_in` incluye la URL
del aviso como variable `{{2}}`, así que el aviso debe estar publicado antes
de enviar esta plantilla a un cliente real.

**El orden de trabajo no es el orden numérico: haz el #9 antes que este.**

Si necesitas avanzar sin el aviso listo, se puede registrar la plantilla con
la variable `{{2}}` sin definir su valor final (Meta aprueba el formato, no el
contenido de las variables) y llenar la URL al momento del envío.

## Criterio de aceptación

- [ ] Ambas plantillas en estatus **APPROVED**
- [ ] Documentadas en `docs/plantillas-hsm.md` con nombre, idioma y variables
