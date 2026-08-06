## Depende de

- #79 — línea base medida

## Objetivo

Bajar el MSPC juntando en un solo mensaje pasos que hoy viajan separados.

**Delta de MSPC esperado: -2 a -3.**

## Qué se puede fusionar

Un mensaje interactivo de WhatsApp admite un `body` largo más botones. Hoy se
desperdicia mandando una pregunta por mensaje.

| Hoy (2 mensajes) | Fusionado (1 mensaje) |
|---|---|
| "Carrito: 10 bolsas de 5kg" + "¿Agregar más?" / luego "¿Qué dirección?" | Carrito + "¿Agregar algo más, o mando a {dirección}?" con botones `Confirmar`, `Agregar más`, `Otra dirección` |
| Resumen del pedido / luego "¿Confirmas?" | Resumen completo con botones `Confirmar`, `Modificar`, `Cancelar` en el mismo mensaje |

## Lo que NO se debe fusionar

Pasos donde la respuesta del cliente **cambia lo que hay que preguntar
después**. `SELECCIONANDO_PRODUCTO` y `CAPTURANDO_CANTIDAD` no se pueden juntar
en dos mensajes independientes porque la cantidad se pregunta *sobre* el
producto elegido. Para eso está el issue #81 (Interactive List).

## Límites de la plataforma

- `body` de mensaje interactivo: **1024 caracteres**
- Reply Buttons: **máximo 3**, con 20 caracteres de título cada uno

Si al fusionar se necesitan más de 3 opciones, el camino es List Message
(issue #81), no partir el mensaje otra vez.

## Riesgo a vigilar

Un mensaje que hace tres preguntas a la vez confunde y **aumenta** los errores
de captura, que cuestan más mensajes que los que se ahorraron. Si el MSPC no
baja tras el cambio, revertir.

## Fusionar el mensaje no es fusionar el estado

La FSM conserva sus estados separados; lo que cambia es cuántos mensajes se
envían al transicionar. Colapsar los estados haría el flujo imposible de
depurar y rompería el botón "Volver" del issue #44.

## Criterio de aceptación

- [ ] `AGREGAR_MAS_O_CONTINUAR` y `CAPTURANDO_DIRECCION` viajan en un mensaje
- [ ] Resumen y confirmación viajan en un mensaje
- [ ] Ningún `body` supera 1024 caracteres
- [ ] Los estados de la FSM siguen siendo distinguibles
- [ ] MSPC re-medido y comparado contra #79
