## Objetivo

Cumplir con la LFPDPPP: aviso de privacidad público y mecanismo verificable de
consentimiento.

## Contexto legal

La Ley Federal de Protección de Datos Personales en Posesión de los
Particulares obliga a informar qué datos se recaban, para qué, y a dar un
canal para ejercer derechos ARCO (Acceso, Rectificación, Cancelación,
Oposición).

Este sistema almacena: número de teléfono, nombre, direcciones de entrega,
coordenadas de ubicación e historial de pedidos. Todo eso es dato personal.

## Contenido mínimo del aviso

1. Identidad y domicilio del responsable (Hielon de León)
2. Datos personales que se recaban
3. Finalidades: procesar pedidos, coordinar entregas, enviar recordatorios
4. Que el tratamiento incluye mensajería automatizada por WhatsApp
5. Medios para ejercer derechos ARCO (correo de contacto)
6. Cómo revocar el consentimiento de recordatorios

## Mecanismo de opt-in

- El campo `clientes.opt_in_recordatorios` arranca en FALSE por defecto
- Pasa a TRUE solo con respuesta afirmativa a `bienvenida_opt_in` (issue #8)
- Se guarda evidencia: el `whatsapp_message_id` de la respuesta y su timestamp
- Escribir "BAJA" o "STOP" debe regresarlo a FALSE

## Criterio de aceptación

- [ ] Aviso de privacidad publicado en una URL pública y estable
- [ ] Flujo de opt-in definido y documentado
- [ ] Definido cómo se registra la evidencia del consentimiento en la BD
- [ ] Definida la palabra clave de baja y su comportamiento

## Nota

No requiere abogado para v1, pero el texto debe revisarlo Gabriel antes de
publicarse, porque el responsable legal es el negocio.
