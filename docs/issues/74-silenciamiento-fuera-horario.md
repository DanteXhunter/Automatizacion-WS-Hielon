## Idea de backlog

Si un cliente insiste escribiendo repetidamente fuera de horario, responder
una sola vez y silenciarse hasta la apertura, en vez de la mitigación básica
de v1 (issue #45) que limita la respuesta a una vez por hora.

## Alcance futuro

- Contador de mensajes fuera de horario por cliente, con ventana de tiempo
  más amplia (por ejemplo, silencio total tras el primer aviso hasta la
  siguiente apertura)
- Evitar gastar cuota de mensajería en algo que no avanza ningún flujo

## Por qué no en v1

La mitigación de una vez por hora ya cubre el caso principal (evitar spam de
respuestas idénticas) con una implementación mínima. El silenciamiento total
es una optimización de costo/ruido que se justifica con volumen real de uso
fuera de horario, dato que todavía no existe.
