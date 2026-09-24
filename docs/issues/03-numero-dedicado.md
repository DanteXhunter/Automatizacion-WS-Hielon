## Objetivo

Dejar el número comercial de Hielon listo para operar con WhatsApp Business y
Cloud API mediante Coexistence, sin perder la atención manual.

## Advertencia crítica actualizada

El camino preferido es **Coexistence**, que permite conservar WhatsApp
Business y conectar el mismo número a Cloud API. No debe iniciarse el registro
definitivo hasta comprobar que la cuenta y el número son elegibles y que el
onboarding ofrece explícitamente esa modalidad.

Un registro estándar de Cloud API sí puede retirar el número de la aplicación;
por eso no se debe asumir que cualquier alta conserva el acceso móvil.

Consecuencias:

- NO usar el número personal de Gabriel.
- NO migrar el número comercial por el flujo estándar si se pretende operar
  con Coexistence.
- Verificar primero que Gabriel pueda conservar y utilizar WhatsApp Business
  para atender handoffs.

## Opciones

1. **Coexistence con el número de Hielon** (opción elegida). El bot opera por
   Cloud API y Gabriel conserva WhatsApp Business para atención manual.
2. **Cloud API sin Coexistence** (contingencia). Requiere una bandeja propia o
   externa para responder; no se adopta sin revisar antes el impacto operativo.

## Requisitos técnicos del número

- Debe estar activo en WhatsApp Business y cumplir los requisitos que Meta
  muestre para Coexistence
- Debe poder recibir SMS o llamada de voz para el código de verificación
- Formato E.164 para la configuración: `+5214771234567`

## Criterio de aceptación

- [ ] Decisión tomada y acordada con Gabriel sobre cuál de las dos opciones
- [ ] Número disponible y con capacidad de recibir el código de verificación
- [ ] Número anotado en formato E.164 en la documentación interna
- [ ] Elegibilidad de Coexistence comprobada antes de registrar el número
- [ ] Comprobado que la aplicación de WhatsApp Business conserva el acceso al
      número después del alta
