## Objetivo

Conseguir un número telefónico exclusivo para el bot.

## Advertencia crítica

Al registrar un número en Cloud API, **se pierde el acceso desde la app de
WhatsApp Business**. El número deja de existir en el celular: solo responde a
través de la API.

Consecuencias:

- NO usar el número personal de Gabriel.
- NO migrar el número comercial que los clientes ya conocen sin tener listo el
  handoff humano (Fase 4). Si se migra antes, nadie del equipo podrá contestar
  manualmente a un cliente que lo necesite.

## Opciones

1. **Número nuevo dedicado** (recomendado para v1). Se le comunica a los
   clientes como "línea de pedidos automatizada". El número actual sigue
   funcionando normal en el celular para casos humanos.
2. **Migrar el número existente.** Mejor experiencia para el cliente, pero
   obliga a tener el panel/handoff funcionando desde el día uno.

## Requisitos técnicos del número

- No puede estar registrado actualmente en WhatsApp (o hay que borrar esa
  cuenta primero)
- Debe poder recibir SMS o llamada de voz para el código de verificación
- Formato E.164 para la configuración: `+5214771234567`

## Criterio de aceptación

- [ ] Decisión tomada y acordada con Gabriel sobre cuál de las dos opciones
- [ ] Número adquirido y con capacidad de recibir el código de verificación
- [ ] Número anotado en formato E.164 en la documentación interna
