## Depende de

- #28 — dispatcher que reconoce el estado

## Objetivo

Silenciar al bot únicamente en la conversación que tomó un humano, sin afectar
la atención automática de otros clientes.

## Comportamiento

En `EN_ASESOR_HUMANO`:

1. Todo mensaje entrante se guarda en `mensajes` (texto, imagen, ubicación,
   lo que sea)
2. El bot **no genera ninguna respuesta automática**
3. La conversación no avanza de estado por sí sola

El estado pertenece a la conversación del cliente. No existe una bandera global
que apague el bot completo: si el cliente A está en `EN_ASESOR_HUMANO`, un
mensaje del cliente B debe seguir su propia FSM y recibir respuesta normalmente.

Es el único estado donde llegar aquí no dispara un mensaje saliente
inmediato. El dispatcher debe reconocerlo como caso especial: procesa el
guardado del mensaje pero corta antes de invocar cualquier lógica de envío.

## Por qué no hay timeout automático de salida

Se pensó en regresar a `IDLE` solo si nadie escribe en X horas, pero eso
arriesga que el bot retome justo cuando el humano sigue resolviendo el caso a
mano. Se prefiere una salida explícita (issue #49): mejor pecar de manual que
de automático en el punto donde ya hay una persona involucrada.

## Cómo se entra aquí

Desde `MENU_PRINCIPAL` o `REVISANDO_RESUMEN` con el botón "Hablar con asesor"
(issue #50), o por escalamiento automático (3 entradas inválidas en el menú,
issue #30).

## Cómo se prueba sin los issues #49 y #50

Este handler se cierra forzando el estado a `EN_ASESOR_HUMANO` directamente en
la base de datos (o en el test) y verificando el silencio del bot. Los caminos
de entrada (#50) y de salida (#49) son issues aparte y **no bloquean este**.

## Criterio de aceptación

- [ ] Ningún mensaje saliente se genera mientras el estado sea
      `EN_ASESOR_HUMANO`
- [ ] Los mensajes entrantes se siguen guardando con su idempotencia normal
- [ ] El estado no cambia solo por el paso del tiempo
- [ ] Test que confirme cero llamadas al cliente de WhatsApp en este estado
- [ ] Test con dos clientes simultáneos: uno permanece silenciado en handoff y
      el otro recibe la respuesta automática correspondiente a su estado
