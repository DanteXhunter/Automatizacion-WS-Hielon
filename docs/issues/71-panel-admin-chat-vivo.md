## Decisión de alcance actualizada

El proyecto tendrá un **panel web sencillo**, pero se desarrollará al final,
después de completar pedidos, persistencia, consulta de conversaciones y
handoff. My Business POS 2011 continuará como sistema administrativo y punto de
venta; este panel no implementará caja, inventario ni facturación.

## Por qué resuelve un problema real

Con Coexistence, Gabriel atiende manualmente desde WhatsApp Business. El panel
complementa esa operación mostrando pedidos, conversaciones, historial y el
estado del handoff. Si Coexistence no resulta elegible, el alcance deberá
ampliarse para permitir respuestas manuales mediante Cloud API.

## Alcance del panel sencillo

- Lista y detalle de pedidos.
- Lista y detalle de conversaciones.
- Historial de mensajes.
- Identificación y cierre de handoffs.
- Consumo de endpoints administrativos previamente probados desde Swagger.
- Enlace claro entre el folio del bot y la captura manual en My Business POS
  2011, sin duplicar funciones de caja, inventario o facturación.

Un inbox multiusuario en tiempo real con asignación de agentes, notas internas
y WebSockets/SSE sigue siendo una evolución posterior.

## Criterio de aceptación

- [ ] La secretaria puede localizar pedidos pendientes y abrir su detalle
- [ ] Se puede consultar el historial completo de una conversación
- [ ] Las conversaciones en handoff se distinguen y pueden cerrarse
- [ ] Cerrar un handoff devuelve al bot solo esa conversación
- [ ] El panel no implementa caja, inventario, facturación ni impresión fiscal
