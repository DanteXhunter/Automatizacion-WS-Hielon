## Depende de

- #1 — Business Manager creado

## Objetivo

Completar la verificación de negocio en Meta para levantar los límites de
mensajería y poder usar un número propio en producción.

## Contexto

Sin verificar, la cuenta queda en modo restringido: pocos destinatarios únicos
por día y sin acceso a número propio en producción. La verificación la revisa
un humano de Meta y **tarda de 1 a 5 días hábiles**.

Es la dependencia externa más lenta del proyecto. Arrancar de inmediato.

## Documentos requeridos (México)

- Constancia de situación fiscal (SAT)
- Comprobante de domicilio del negocio a nombre de la empresa
- Opcionalmente, acta constitutiva si es persona moral

Los datos deben coincidir **exactamente** con el nombre dado de alta en el
issue #1. Cualquier diferencia de razón social provoca rechazo.

## Criterio de aceptación

- [ ] Documentos subidos en Business Settings > Security Center
- [ ] Estatus "Verificado" en el Business Manager
- [ ] Si es rechazado, se documenta el motivo y se reintenta

## Desbloqueo mientras tanto

No esperar a que termine. Meta entrega un **número de prueba** gratuito al
crear la app (issue #4) que funciona sin verificación y permite hasta 5
destinatarios de prueba. Con eso se desarrollan completas las Fases 1, 2 y 3.

## Actualización

Al entrar a Security Center, Meta mostró: "Tu organización no tiene que
completar la verificación". Esto es normal para una cuenta nueva con poco
volumen: Meta solo exige verificación cuando se necesita subir el límite de
mensajería más allá del tier inicial, usar un nombre de perfil que no
coincida con el dominio, o solicitar Meta Verified.

**Issue pospuesto, no completado.** Se retoma cuando ocurra alguno de estos
triggers:
- Se topa el límite diario de destinatarios únicos al escalar el envío real
- Se registra el número dedicado de producción y Meta sí lo pide en ese punto
- Se activa el recordatorio matutino a la base completa de clientes

Mientras tanto, avanzar con los issues #4 y #5, que no dependen de esto.
