## Idea de backlog

Investigar y, solo si existe un mecanismo seguro y soportado, automatizar el
registro de pedidos confirmados en **My Business POS 2011** y la impresión del
ticket en la computadora del negocio.

## Situación actual

My Business POS 2011 sí existe y es el sistema administrativo de Hielon. La
versión está descontinuada y el fabricante ya no le brinda soporte. La
documentación pública confirma que usa SQL Server y que la familia del producto
incluye mecanismos de programación e importación, pero todavía no demuestra
cuál de ellos permite crear una venta completa de forma soportada en esta
instalación concreta.

Hasta resolverlo, la secretaria consulta el pedido confirmado, lo captura
manualmente en el POS y desde ahí imprime el ticket.

## Investigación obligatoria

- Identificar edición, compilación, licencia y módulos instalados.
- Respaldar la base antes de cualquier prueba.
- Revisar procedimientos, formularios, importaciones, scripts o SDK disponibles
  en la instalación y documentación original.
- Confirmar con una venta de prueba cuál es el mecanismo soportado para generar
  folio, afectar inventario, registrar pago e imprimir ticket.
- Mapear productos del bot con las claves reales del catálogo del POS.
- Documentar qué eventos y campos son obligatorios para una venta válida.

## Arquitectura candidata

Si la investigación lo permite, un servicio puente en la computadora Windows
del POS recibirá o consultará pedidos confirmados, los registrará mediante la
interfaz soportada, solicitará la impresión y devolverá al backend el folio y
resultado del POS.

El `numero_orden` del bot será la llave de idempotencia: reintentar una solicitud
no puede crear dos ventas ni imprimir dos tickets. Las fallas quedan en cola
para reintento o captura manual.

## Límites de seguridad

- No escribir directamente en tablas internas sin contrato documentado.
- No automatizar clics de la interfaz como primera opción.
- No exponer SQL Server a Internet.
- No bloquear el flujo manual si el puente o la conexión fallan.

## Criterio de aceptación

- [ ] Capacidades reales de la instalación documentadas con evidencia
- [ ] Mecanismo de integración soportado identificado, o decisión explícita de
      conservar la captura manual
- [ ] Prueba en ambiente controlado crea una sola venta y un solo ticket
- [ ] Reintentar el mismo `numero_orden` no duplica la venta
- [ ] Una falla deja el pedido disponible para captura manual
- [ ] Se documentan respaldo, rollback y operación para la secretaria
