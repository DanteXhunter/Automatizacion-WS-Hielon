# Automatizacion WS Hielon — Contexto del Proyecto

## Sobre este documento

Este archivo es la memoria del proyecto. Contiene todo el contexto de negocio, decisiones de arquitectura, requisitos, modelo de datos, máquina de estados y roadmap. Sirve para dos propósitos:

1. Que Claude Code (o cualquier IA/desarrollador que retome el proyecto) tenga contexto completo sin tener que reconstruirlo.
2. Que el desarrollador humano tenga una fuente única de verdad de por qué se tomaron las decisiones.

**Actualizar este documento cuando cambien decisiones. Es documentación viva.**

---

## Sobre el desarrollador

- Estudiante de Ingeniería de Software y Sistemas Computacionales en Universidad De La Salle Bajío, León, Guanajuato.
- Perfil técnico: sólido en Python, comparativamente débil en Node.js/Express.
- Este es su primer proyecto de automatización de chat y de webhooks. Nunca ha trabajado con WhatsApp API.
- No trabaja con Docker aún; está aprendiendo.
- Prefiere entender el panorama antes de saltar a herramientas.
- Estilo de comunicación: español informal, directo, sin redundancia, con explicación de conceptos técnicos cuando se introducen.

### Nivel técnico real (calibrado 6-ago-2026)

- **Python**: sólido a nivel de lenguaje. Sabe qué es una clase, un diccionario, un módulo.
- **Backend**: ha visto APIs y entiende el concepto de endpoint y CRUD, pero **nunca ha construido una desde cero**. Este es su primer backend real.
- **Sin experiencia en**: producción/despliegue, tests (nunca ha escrito uno con pytest), async, Docker, PostgreSQL más allá de lo básico.
- **Modo de trabajo acordado**: Claude escribe el código comentado y lo explica; el usuario lo estudia, lo corre y lo cuestiona. **No** escribe el código él desde cero — todavía.
- **Prueba de avance acordada**: al terminar cada issue, el usuario debe poder explicar, sin abrir el código, qué hace ese archivo, por qué existe y qué se rompe si lo borra. Si no puede, no se avanza al siguiente issue.
- **Estilo de aprendizaje**: cuestiona las analogías y encuentra sus contradicciones. No acepta explicaciones que salten pasos. Cuando dice "no entendí", el problema suele ser que se explicó **para qué sirve** algo en vez de **cómo funciona mecánicamente** — bajar un nivel de abstracción, no repetir con otras palabras.

### Conceptos ya explicados y comprendidos (no re-explicar desde cero)

Webhook y por qué existe (polling vs. push) · los dos canales HTTP separados (webhook de entrada / Graph API de salida) y quién es servidor en cada uno · GET de verificación vs. POST de mensajes · endpoint vs. petición · `async`/`await`, event loop, concurrencia vs. paralelismo, por qué no es "segundo plano" · proceso vs. programa · variables de entorno, `os.environ`, herencia del entorno, rol del `.env` vs. Railway · type hints y por qué Python los ignora · Pydantic, `BaseModel`, `BaseSettings`, `validate_call`, validación y conversión · herencia de clases.

### Preguntas de arranque de cada issue

El usuario pidió que **cada archivo nuevo** se presente respondiendo estas cuatro preguntas. Es el formato estándar del proyecto:

1. ¿Qué va a contener?
2. ¿Dónde vive y por qué ahí?
3. ¿Por qué se le asignó ese nombre?
4. ¿Por qué se crea en esta etapa y no antes o después?

## Sobre el negocio

- **Empresa**: Hielon de León — startup de fabricación de hielo en León, Guanajuato, México.
- **Dueño**: Gabriel Rojas González.
- **Grupo empresarial**: Hielon (hielo) + Cerpomex (carne) + Fruvec (fruta y verdura). El sistema debe diseñarse pensando que en el futuro puede escalarse a los otros negocios (multi-tenancy en modelo de datos).
- **Clientela**: mayoristas recurrentes (restaurantes, tienditas, negocios que revenden) y ocasionales (eventos, bodas). Pedidos pequeños individuales no son foco (regla de pedido mínimo, ver más abajo).
- **Horario laboral**: lunes a sábado, 7:00–17:00. Domingo cerrado.
- **Corte de aceptación para el día**: 14:00. Después de esa hora, el bot sugiere programar para mañana; si el cliente insiste, la decisión final es humana.

## Objetivo del proyecto

Automatizar el chat de WhatsApp del negocio para:
1. Recibir y registrar pedidos sin intervención humana en el flujo estándar.
2. Enviar recordatorios matutinos proactivos preguntando si el cliente necesita hielo hoy.
3. Rutear a un humano cuando el caso lo requiera (negociación, regateo, casos raros).

Los datos capturados por el bot alimentarán en el futuro el ERP interno (fuera del alcance de este proyecto).

---

## Alcance — qué es y qué NO es este proyecto

**Este repo es el backend del bot de WhatsApp. Nada más.** Concretamente:

**Dentro del alcance:**
- Endpoint HTTPS público que recibe webhooks de Meta y valida su firma.
- Máquina de estados que conduce la conversación y captura el pedido.
- Persistencia en PostgreSQL de clientes, pedidos, conversaciones y mensajes.
- Envío de mensajes salientes vía Meta Cloud API.
- Notificación a un humano (WhatsApp) cuando el bot debe callarse.

**Fuera del alcance — proyectos separados que consumirán esta base de datos:**
- **ERP / panel administrativo con frontend.** Ver mensajes en tiempo real, chat en vivo del asesor humano, autenticación de usuarios internos, roles y permisos, catálogo, inventario, rutas de reparto. Es un segundo proyecto con su propio repo. Este backend debe dejarlo *posible* (datos bien modelados, endpoints admin limpios), no *implementarlo*.
- **Integración con el ERP existente del grupo**, si lo hay.
- **Multi-tenancy real** para Cerpomex y Fruvec. Se contempla en el modelo de datos, no se implementa en v1.

**Por qué importa la separación**: el handoff a humano en v1 se resuelve por una notificación de WhatsApp a Gabriel precisamente porque el panel de chat en vivo es otro proyecto. Si se mezclan, ninguno de los dos se termina. La regla es: **este backend termina donde empieza la interfaz humana**.

**Objetivo de negocio**, además del ahorro operativo: es una pieza de credibilidad comercial. Gabriel la muestra en juntas con restaurantes y hoteles como prueba de que Hielon es una operación seria y lista para atender volumen. Eso implica que el bot debe verse pulido y no fallar en la demo, aunque el volumen real todavía sea bajo.

---

## Estado actual y riesgos (6-ago-2026)

**Fecha objetivo de entrega**: finales de agosto a mediados de octubre de 2026 (~10 semanas). Cuadra con el roadmap completo, incluyendo n8n y dashboard de costos.

**Estado por fase:**
- **Fase 0 — BLOQUEADA.** La cuenta de Meta Business existe pero **fue baneada por razones desconocidas**. Ticket de apelación levantado; respuesta esperada ~7-ago-2026.
- **Fase 1 — desbloqueada y en curso.** El webhook, la validación HMAC, la config y los tests se desarrollan sin cuenta de Meta. Solo la prueba end-to-end con un mensaje real requiere la cuenta viva.

**Riesgo #1 del proyecto: el baneo.** Las apelaciones de Meta Business a veces no se revierten y pueden tardar mucho más de lo prometido. Si no se recupera, el plan B es abrir cuenta con otro administrador o bajo otra razón social del grupo (Cerpomex, Fruvec). No dejar que este bloqueo detenga el desarrollo del backend.

**Ya resuelto**: número dedicado adquirido; Gabriel sabe y aceptó que ese número pierde la app móvil de WhatsApp.

**Pendiente de dato**: precio de lista de las bolsas de 3, 5 y 10 kg. Se necesita para calcular qué porcentaje del ticket representan los MX$1.10 de mensajería y decidir cuánto vale la pena optimizar (ver "Presupuesto de mensajes").

---

## Cómo se construye el repositorio — estructura incremental

**Decisión (6-ago-2026): la estructura de carpetas NO se crea completa de golpe.** El issue 10 se recortó.

El árbol completo documentado más abajo es un **mapa de destino**, no una tarea de creación. En disco solo existe lo que ya se usa.

**Regla: un archivo nace cuando su ausencia duele.** Se escribe el código donde quepa, y cuando el archivo se pone incómodo, se extrae lo que corresponde. Así se entiende *por qué* existe cada separación en vez de rellenar huecos de una plantilla.

**Por qué**, dado que el objetivo es aprender: 30 carpetas vacías con `__init__.py` no enseñan nada y producen la sensación de trabajar dentro de un molde ajeno. El costo de mover código a su lugar definitivo después es trivial; el costo de la estructura prematura es no aprender.

**Fase 1 — archivos que sí existen** (5, nada más):

```
src/main.py                 ← ensamblaje de la app FastAPI
src/config.py               ← Settings con Pydantic BaseSettings
src/api/webhook.py          ← GET de verificación + POST de mensajes
src/whatsapp/signature.py   ← validación HMAC (función pura, testeable)
src/whatsapp/client.py      ← wrapper httpx sobre la Graph API
```

`models/`, `fsm/`, `services/`, `notifications/`, `utils/` **no existen** hasta que su fase los necesite.

**Layout `src/`**: se adopta porque es el estándar de la industria en Python. La razón técnica de fondo (resolución de imports y el fallo "en mi máquina sí jala") se explica en la Fase 5, cuando se despliegue y el problema sea tangible. Pendiente explícitamente diferido, no olvidado.

---

## Restricciones técnicas críticas — leer antes de tocar código

### 1. Meta Cloud API — un solo canal legítimo

WhatsApp le pertenece a Meta. La única vía legal para automatizar mensajería es la **WhatsApp Cloud API** de Meta (Graph API). Alternativas como Baileys o `whatsapp-web.js` violan los términos y llevan a baneo del número. No se usan.

### 2. Regla de las 24 horas y plantillas (HSM)

- Cuando el cliente escribe primero, se abre una **ventana de sesión de 24 h** donde el bot puede responder **texto libre, sin plantilla, gratis** (categoría `service`).
- Fuera de esa ventana, solo se puede enviar **plantillas** (HSM = Highly Structured Message, nombre técnico interno; en el panel de Meta aparece como "Message Template") pre-aprobadas.
- **Consecuencia directa**: el recordatorio matutino de 6 am, al no tener ventana abierta, **debe ser una plantilla aprobada**, categoría `utility`. Modificar el texto = crear una plantilla nueva y re-aprobar (1 hora a 3 días).
- **Modelo de cobro vigente para este proyecto — el de 1 de octubre de 2026.** Todo el sistema se diseña contra este modelo, no contra el anterior. El modelo viejo ("todo gratis dentro de la ventana de 24h") muere el 30 de septiembre de 2026; construir sobre él sería construir algo con dos meses de vida útil.
- **Categorías y costo en México** (base rate Meta, sin BSP, IVA no incluido):

  | Categoría | Qué es | Costo desde 1-oct-2026 |
  |---|---|---|
  | `service` | Texto libre dentro de la ventana de 24h (todo el flujo del bot) | **MX$0.1565 / mensaje** (~USD $0.0085) |
  | `utility` | Transaccional: recordatorio, confirmación, status | **MX$0.1565 / mensaje**, dentro o fuera de ventana |
  | `authentication` | OTPs. No aplica a este proyecto | **MX$0.1565 / mensaje** |
  | `marketing` | Promocional, requiere opt-in específico | **~USD $0.0436 / mensaje** (~5x más caro) |
  | `Meta Business Agent` | IA propia de Meta que procesa y responde el mensaje por ti. Cobro doble: tokens (~USD $2.00 / millón) + el envío | **No se usa en este proyecto** |

- **Lo que cambia respecto al modelo anterior**: antes cada conversación tenía un costo de apertura y el resto de los mensajes de la ventana eran gratis. Ahora **se cobra por mensaje saliente, uno por uno, sin importar la ventana**. `service` deja de ser gratis y pasa a costar lo mismo que `utility`. Meta ya no da descuento por volumen en `service`: la tarifa es plana.
- **Consecuencia de arquitectura, no de contabilidad**: cada mensaje que el bot envía es dinero. El diseño de la FSM deja de optimizarse solo por claridad conversacional y pasa a optimizarse por **mensajes salientes por pedido completado**. Ver "Presupuesto de mensajes" abajo.
- **Meta Business Agent** (quinta categoría, activa desde el 1 de agosto de 2026): Meta intercepta el mensaje, lo procesa con su propio LLM y genera la respuesta. Se descarta explícitamente: cobra dos veces (procesamiento por tokens + envío), y el objetivo del proyecto es una FSM determinista bajo nuestro control, no delegar la conversación a un tercero.
- **Importante**: la categoría se define por el **contenido** de la plantilla (Meta la revisa y puede reclasificar), no por a quién se le envía. Evitar lenguaje promocional ("oferta", "descuento", "aprovecha") en plantillas utility para no ser reclasificadas a marketing (5x más caro).
- **Regla práctica de envío**: mensajes dentro de la conversación activa del bot (todo el flujo de captura de pedido) → siempre texto libre (`service`), nunca plantilla. Plantilla solo para lo que se envía sin que el cliente haya escrito recientemente (recordatorio matutino, o notificaciones sobre pedidos programados para otro día donde la ventana ya cerró). Esto ya **no** se hace por ahorro (cuestan igual) sino porque fuera de ventana la plantilla es obligatoria.
- **Los mensajes entrantes no se cobran.** Solo se paga lo que el negocio envía. Cualquier estrategia de ahorro consiste en reducir mensajes salientes, nunca en limitar lo que el cliente escribe.
- **Límite de conversaciones iniciadas por el negocio**: 250 clientes únicos por ventana rodante de 24h sin verificar el negocio; sube a 1,000+ tras verificación (Tier 1). No es un cupo diario que se reinicia a medianoche — se libera de forma continua conforme pasan 24h desde cada envío.

### 2.1 Presupuesto de mensajes — restricción de diseño de primera clase

**Métrica del proyecto: mensajes salientes por pedido completado (MSPC).** Se mide, se reporta en el dashboard de costos (Fase 6.1) y se usa para aceptar o rechazar cambios en la FSM.

Cálculo del flujo tal como está diseñado hoy (cliente conocido, un solo producto, sin errores):

| # | Mensaje saliente | Estado |
|---|---|---|
| 1 | Saludo + menú principal | `IDLE` → `MENU_PRINCIPAL` |
| 2 | Botones de producto | `SELECCIONANDO_PRODUCTO` |
| 3 | "¿Cuántas bolsas?" | `CAPTURANDO_CANTIDAD` |
| 4 | Carrito + ¿agregar más? | `AGREGAR_MAS_O_CONTINUAR` |
| 5 | ¿Qué dirección? | `CAPTURANDO_DIRECCION` |
| 6 | Resumen + confirmar | `REVISANDO_RESUMEN` |
| 7 | "Pedido #2026-0142 confirmado" | → `IDLE` |

**7 mensajes = MX$1.10 por pedido**, en el mejor caso. Con un error de captura o un "volver" sube a 9-10. A 40 pedidos/día × 26 días: **~MX$1,150/mes solo en el flujo de pedido**, más los recordatorios matutinos (50 clientes × 26 días × MX$0.1565 = **MX$203/mes**, se pague o no con pedido).

Bajo el modelo anterior esto costaba casi nada. Bajo el nuevo, es un gasto operativo real que hay que justificar frente al costo de que una persona tome el pedido.

**Estrategias de reducción a evaluar antes de escribir los handlers de la Fase 3** (ninguna está cerrada todavía; se decide con datos, no por intuición):

1. **Fusionar estados en un solo mensaje.** El mensaje de WhatsApp admite `body` largo + botones. `AGREGAR_MAS_O_CONTINUAR` y `CAPTURANDO_DIRECCION` pueden viajar juntos; el resumen y la confirmación también. Objetivo realista: bajar de 7 a 4-5.
2. **Interactive List en vez de Reply Buttons encadenados.** Una List Message soporta hasta 10 opciones en un solo envío: producto y cantidad frecuente ("5 kg × 10") pueden ser una sola selección en vez de dos mensajes.
3. **Atajo para el cliente recurrente.** Si el cliente tiene un pedido anterior, el primer mensaje ya ofrece "¿Repetimos lo de siempre: 10 bolsas de 5 kg a la dirección X?" con botones Sí/Cambiar. Camino feliz de **2 mensajes** en vez de 7. Este es el ahorro más grande y encaja con el perfil de clientela (mayoristas recurrentes).
4. **No responder a todo.** Entradas inválidas no siempre merecen un mensaje de error propio; se puede reenviar el prompt con la corrección incluida, y no responder nada a mensajes irrelevantes dentro de la ventana.
5. **Recordatorio matutino segmentado, no masivo.** En vez de mandarlo a todos los clientes con opt-in cada día, mandarlo según patrón de compra (frecuencia histórica, días que suele pedir). Un cliente que compra los martes no necesita 6 recordatorios semanales.
6. **Batching de confirmaciones.** Notificaciones de status (en ruta, entregado) agrupadas o suprimidas si el cliente no las pidió.

**Regla de revisión**: cada issue de la Fase 3 que agregue un mensaje saliente al flujo debe declarar en su descripción el delta de MSPC y por qué se justifica.

### 3. Un número no puede estar en Cloud API y en la app WhatsApp Business a la vez

Al registrar el número en Cloud API, se pierde el acceso desde la app móvil. Si Gabriel o un vendedor quiere responder desde ese mismo número, debe ser desde el panel que se construya. En v1 el handoff a humano se resuelve notificando al WhatsApp personal de Gabriel (ver sección de handoff).

### 4. LFPDPPP (Ley Federal de Protección de Datos Personales, México) y opt-in

- El cliente debe dar **consentimiento explícito documentado (opt-in)** para recibir mensajes proactivos del negocio. Se pide en el primer contacto del cliente nuevo y se guarda con fecha, hora, canal y texto exacto aceptado.
- El opt-in para **marketing es distinto y adicional** al opt-in básico — se pregunta por separado ("¿deseas también recibir promociones?"). No usar el mismo consentimiento para ambos.
- Debe existir un aviso de privacidad accesible (link que el bot pueda enviar si el cliente lo pide).
- No se guardan datos sensibles en logs (números de tarjeta, etc.).
- Sin opt-in documentado: riesgo legal (LFPDPPP) y riesgo de plataforma (reportes/bloqueos bajan el tier de calidad del número en Meta).

### 5. Race conditions — serialización por cliente

Dos mensajes del mismo cliente pueden llegar casi al mismo tiempo al webhook. Sin serialización, la lógica lee estado obsoleto y sobrescribe. **Se resuelve con advisory locks de PostgreSQL** (`pg_advisory_lock`) usando el `cliente_id` como clave.

### 6. Validación de webhook de Meta

Meta firma cada request al webhook con **HMAC-SHA256** en el header `X-Hub-Signature-256`. El backend **debe validar esta firma antes de procesar el body**. Sin esto, cualquiera puede inyectar mensajes falsos.

### 7. Idempotencia

Meta puede reintentar entregar el mismo webhook. Cada mensaje trae un `message_id` único. Guardar los `message_id` procesados y descartar duplicados.

---

## Stack técnico y justificación

| Componente | Tecnología | Justificación |
|---|---|---|
| Backend web | **FastAPI** (Python) | Framework moderno, async nativo, Pydantic para validación, Swagger autogenerado. Alineado con el perfil Python del desarrollador. |
| Servidor ASGI | **Uvicorn + Gunicorn** | Estándar para FastAPI en producción. |
| Base de datos | **PostgreSQL** | Datos relacionales (clientes, pedidos, items, direcciones); transaccional; alineado con el ERP futuro. |
| ORM | **SQLModel** | Del autor de FastAPI, integra Pydantic + SQLAlchemy; menor boilerplate que SQLAlchemy puro. |
| Migraciones | **Alembic** | Estándar de facto en Python para versionar esquema. |
| Driver DB | **asyncpg** | Driver async de Postgres. |
| Cliente HTTP | **httpx** | Cliente HTTP async, moderno. Usar para llamar a Meta Cloud API. |
| Automatizaciones | **n8n** | Cron matutino de recordatorios, futura sincronización con ERP. Auto-hospedable. |
| Hosting | **Railway** | Deploy automático desde GitHub, PostgreSQL incluido, HTTPS y subdominio gratis (`*.up.railway.app`) sin configuración manual. Elegido sobre AWS por ser desproporcionado en complejidad para el volumen del proyecto (30-50 pedidos/día); sin costo de dominio propio en v1. |
| Dominio | Subdominio gratuito de Railway (v1) | No se compra dominio propio en v1; el webhook de Meta solo necesita un endpoint HTTPS válido, no importa si está indexado o tiene sitio web. Revisar dominio propio (~$12 USD/año) si el proyecto pasa a producción definitiva o si el grupo empresarial ya tiene uno registrado. |
| Túnel para desarrollo | **ngrok** | Exponer localhost al webhook de Meta durante desarrollo. |
| Testing | **pytest** + **pytest-asyncio** | Estándar de Python. |
| Validación de datos | **Pydantic** | Ya viene con FastAPI. |
| Serialización por cliente | **PostgreSQL advisory locks** | Simple, sin agregar Redis en v1. |

**Sin LLM en v1.** Todo el flujo se resuelve con máquina de estados determinista.

**Sin Redis en v1.** El estado de conversación vive en Postgres. Si el volumen crece se puede migrar a Redis después.

**Sin panel admin React en v1.** La visualización se hace vía Swagger (`/docs` de FastAPI) y acceso directo a Postgres con DBeaver o similar.

---

## Arquitectura general

```
┌─────────────┐
│   CLIENTE   │
│ (WhatsApp)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   META CLOUD API    │
└──────┬──────────────┘
       │  Webhook POST
       ▼
┌────────────────────────────────────────┐
│   BACKEND FastAPI (Railway)            │
│                                         │
│  - Endpoint /webhook/whatsapp          │
│  - Validación HMAC                     │
│  - Máquina de estados de conversación  │
│  - Advisory lock por cliente_id        │
│  - Handler de mensajes                 │
│  - Cliente a Meta Cloud API            │
└──────┬─────────────────────────────────┘
       │
       ▼
┌─────────────────────┐
│    PostgreSQL       │
│  clientes           │
│  direcciones        │
│  productos          │
│  pedidos            │
│  pedido_items       │
│  conversaciones     │
│  mensajes           │
└─────────────────────┘
       ▲
       │
┌──────┴──────────────┐          ┌─────────────────────┐
│  n8n                │ ────────►│  META CLOUD API     │
│  Cron L-S 6:00 am   │  Plantilla HSM               │
└─────────────────────┘          └─────────────────────┘
```

---

## Modelo de datos (PostgreSQL)

### Tablas

**`clientes`**
- `id` UUID PK
- `telefono` VARCHAR UNIQUE — E.164, ej: `+5214771234567`
- `nombre` VARCHAR NULLABLE
- `opt_in_recordatorios` BOOLEAN DEFAULT FALSE
- `created_at`, `updated_at` TIMESTAMP

**`direcciones`**
- `id` UUID PK
- `cliente_id` UUID FK → clientes.id
- `texto` TEXT NULLABLE — dirección en texto libre
- `latitud` DECIMAL NULLABLE
- `longitud` DECIMAL NULLABLE
- `es_ultima_usada` BOOLEAN — se marca la más reciente para reutilización rápida
- `created_at` TIMESTAMP

**`productos`**
- `id` UUID PK
- `nombre` VARCHAR — ej: "Bolsa 5 kg"
- `peso_kg` DECIMAL — 3, 5, 10
- `dimensiones` VARCHAR — ej: "30 x 60 cm"
- `precio` DECIMAL — precio fijo, sin IVA, sin envío
- `activo` BOOLEAN

**`pedidos`**
- `id` UUID PK
- `numero_orden` VARCHAR UNIQUE — ej: "2026-0142", legible
- `cliente_id` UUID FK
- `direccion_id` UUID FK
- `estado` ENUM — `borrador`, `pendiente`, `programado`, `en_ruta`, `entregado`, `cancelado_cliente`, `cancelado_negocio`
- `fecha_entrega` TIMESTAMP NULLABLE — para pedidos programados (v2)
- `observaciones` TEXT — texto libre; incluye posible hora sugerida
- `total` DECIMAL — suma de items
- `created_at`, `updated_at` TIMESTAMP

**`pedido_items`**
- `id` UUID PK
- `pedido_id` UUID FK
- `producto_id` UUID FK
- `cantidad` INTEGER
- `precio_unitario` DECIMAL — snapshot al momento del pedido (por si cambia el precio del catálogo)
- `subtotal` DECIMAL

**`conversaciones`**
- `id` UUID PK
- `cliente_id` UUID FK
- `estado_actual` VARCHAR — nombre del estado FSM
- `estado_anterior` VARCHAR NULLABLE — para "volver al paso anterior"
- `contexto` JSONB — datos temporales del flujo (ej: pedido en borrador, item actual)
- `pedido_borrador_id` UUID FK NULLABLE — pedido en construcción
- `ultima_interaccion` TIMESTAMP
- `version` INTEGER DEFAULT 1 — para optimistic locking si se decide usar

**`mensajes`**
- `id` UUID PK
- `cliente_id` UUID FK
- `direccion` ENUM — `entrante`, `saliente`
- `whatsapp_message_id` VARCHAR UNIQUE — para idempotencia
- `tipo` VARCHAR — `text`, `interactive`, `location`, `image`, etc.
- `contenido` JSONB — payload crudo
- `estado` VARCHAR NULLABLE — `sent`, `delivered`, `read`, `failed` (para salientes)
- `pricing_category` VARCHAR NULLABLE — `service`, `utility`, `marketing`, `authentication`; se llena con el dato que Meta reporta en el webhook de status del mensaje saliente. Fuente para el dashboard de costos propio (ver Fase 6.1).
- `costo_estimado` DECIMAL NULLABLE — costo en MXN del mensaje saliente al momento del envío, calculado con la tarifa vigente en config. Se guarda como snapshot porque las tarifas de Meta cambian y el histórico de gasto debe seguir siendo correcto después de un cambio de precio.
- `pedido_id` UUID FK NULLABLE — permite calcular el MSPC (mensajes salientes por pedido completado) atribuyendo cada mensaje a la conversación de pedido que lo originó.
- `created_at` TIMESTAMP

### Estados del pedido (transiciones válidas)

```
borrador → pendiente        (cliente confirma en el flujo)
borrador → cancelado_cliente (cliente cancela durante captura)
pendiente → programado       (si tiene fecha_entrega futura)
pendiente → en_ruta          (humano despacha)
pendiente → cancelado_negocio (no hay stock, fuera de zona, etc.)
pendiente → cancelado_cliente (cliente cancela antes de despacho)
programado → en_ruta         (llegado el día)
programado → cancelado_*     (antes de despacho)
en_ruta → entregado          (repartidor confirma)
en_ruta → cancelado_negocio  (imposible entregar)
```

Un pedido en `entregado`, `cancelado_cliente` o `cancelado_negocio` es estado terminal — no puede transicionar más.

---

## Máquina de estados de la conversación

### Lista completa de estados (11)

| # | Código | Descripción |
|---|---|---|
| 1 | `IDLE` | Sin interacción activa. Estado por defecto. |
| 2 | `MENU_PRINCIPAL` | Bot mostró opciones: Hacer pedido / Consultar / Modificar / Hablar con asesor. |
| 3 | `SELECCIONANDO_PRODUCTO` | Cliente elige tipo de bolsa (3, 5, 10 kg). |
| 4 | `CAPTURANDO_CANTIDAD` | Cliente indica cuántas bolsas de ese producto. |
| 5 | `AGREGAR_MAS_O_CONTINUAR` | Bot pregunta si agregar otro producto o continuar. |
| 6 | `CAPTURANDO_DIRECCION` | Cliente elige dirección anterior o proporciona una nueva (texto o ubicación WhatsApp). |
| 7 | `REVISANDO_RESUMEN` | Bot muestra resumen, cliente decide confirmar / modificar / cancelar / hablar con asesor. |
| 8 | `SELECCIONANDO_MODIFICACION` | Cliente eligió modificar, dice qué modificar. |
| 9 | `CONFIRMANDO_CANCELACION` | Bot pide confirmación para cancelar el pedido. |
| 10 | `EN_ASESOR_HUMANO` | Bot silenciado, humano interviene. |
| 11 | `FUERA_DE_HORARIO` | Cliente escribió fuera de horario; solo mensaje informativo, no avanza flujo. Nota: puede modelarse como condición en vez de estado; ver "Nota sobre `FUERA_DE_HORARIO`" abajo. |

### Transiciones y mensajes

**Regla global**: si el mensaje llega fuera de horario laboral (dom o L-S antes de 7:00 / después de 17:00), el handler responde con mensaje de horario y no procesa el flujo normal. La conversación queda como estaba.

**Regla global 2**: si en cualquier estado el mensaje del cliente coincide con palabras clave de escape (`cancelar`, `salir`), se ofrece cancelar. En v1 solo se responde "hablar con asesor" desde `MENU_PRINCIPAL` y `REVISANDO_RESUMEN`.

---

#### `IDLE` → recibe mensaje entrante
- Bot verifica si es cliente conocido (por teléfono).
- Bot responde saludo + menú principal.
- Transiciona a → `MENU_PRINCIPAL`.

#### `MENU_PRINCIPAL`
Bot envía Reply Buttons:
- `Hacer pedido` → `SELECCIONANDO_PRODUCTO`
- `Consultar pedido` → busca último pedido pendiente/programado/en_ruta y muestra estado; vuelve a `MENU_PRINCIPAL`
- `Hablar con asesor` → `EN_ASESOR_HUMANO`

Entrada inválida (3 veces) → escala a `EN_ASESOR_HUMANO`.

#### `SELECCIONANDO_PRODUCTO`
Bot envía Reply Buttons:
- `Bolsa 3 kg`
- `Bolsa 5 kg`
- `Bolsa 10 kg`

Selección válida → guarda producto en contexto, transiciona a `CAPTURANDO_CANTIDAD`.

Botón "Volver" → `MENU_PRINCIPAL`.

#### `CAPTURANDO_CANTIDAD`
Bot pregunta: "¿Cuántas bolsas de {producto}?"

Entrada esperada: número entero positivo. Si es "10 kg" con producto de 5 kg, bot debe rechazar pidiendo número de bolsas explícito (no interpretar).

Válido → guarda item en pedido borrador, transiciona a `AGREGAR_MAS_O_CONTINUAR`.

Botón "Volver" → `SELECCIONANDO_PRODUCTO` (borra selección).

#### `AGREGAR_MAS_O_CONTINUAR`
Bot muestra resumen parcial del carrito + Reply Buttons:
- `Agregar otro producto` → `SELECCIONANDO_PRODUCTO`
- `Continuar` → `CAPTURANDO_DIRECCION`

Botón "Volver" → `CAPTURANDO_CANTIDAD` del último item (permite modificar cantidad recién agregada).

#### `CAPTURANDO_DIRECCION`
- Si cliente tiene direcciones previas, bot muestra Reply Buttons con `Usar última dirección` + `Nueva dirección`.
- Si es cliente nuevo (sin direcciones), bot pide directamente nueva dirección.

Entrada esperada:
- Selección "Usar última" → guarda direccion_id, transiciona a `REVISANDO_RESUMEN`.
- Selección "Nueva" o mensaje de texto libre → guarda como texto en nueva dirección.
- Ubicación de WhatsApp → guarda latitud/longitud en nueva dirección.

Válido → `REVISANDO_RESUMEN`.

Botón "Volver" → `AGREGAR_MAS_O_CONTINUAR`.

#### `REVISANDO_RESUMEN`
Bot muestra resumen completo con productos, cantidades, dirección, total. Después de las 14:00, se agrega mensaje sugiriendo programar para mañana. Reply Buttons:
- `Confirmar pedido` → guarda pedido como `pendiente`, asigna `numero_orden`, mensaje de agradecimiento con número de orden (para cliente nuevo especialmente); transiciona a `IDLE`.
- `Modificar pedido` → `SELECCIONANDO_MODIFICACION`
- `Cancelar pedido` → `CONFIRMANDO_CANCELACION`
- `Hablar con asesor` → `EN_ASESOR_HUMANO`

#### `SELECCIONANDO_MODIFICACION`
Bot pregunta: "¿Qué deseas modificar?"
Reply Buttons:
- `Productos` → borra todos los items del pedido borrador, `SELECCIONANDO_PRODUCTO`
- `Dirección` → `CAPTURANDO_DIRECCION`

Botón "Volver" → `REVISANDO_RESUMEN`.

Nota v1: no se permite editar items individualmente. Modificar productos = empezar carrito de nuevo.

#### `CONFIRMANDO_CANCELACION`
Bot: "¿Seguro que deseas cancelar tu pedido?"
Reply Buttons:
- `Sí, cancelar` → marca pedido borrador como `cancelado_cliente`, mensaje de despedida, `IDLE`.
- `No, regresar` → `REVISANDO_RESUMEN`.

#### `EN_ASESOR_HUMANO`
- El bot **no responde** mientras esté en este estado.
- Todos los mensajes entrantes se guardan en `mensajes`.
- Se dispara notificación al **WhatsApp personal de Gabriel** con: número del cliente, últimos mensajes, motivo (regateo, escape hatch, etc.). Como Gabriel nunca le escribe al bot, nunca hay ventana de 24h abierta con él: la notificación **debe ser plantilla `utility` aprobada** (`handoff_asesor`). Costo MX$0.1565 por handoff, despreciable.
- **Decisión revisada (6-ago-2026)**: originalmente era Telegram; se cambió a WhatsApp porque Gabriel no usa Telegram. Una notificación que llega a una app que el destinatario no abre no sirve de nada.
- Al cerrar el chat manualmente (endpoint admin), el estado vuelve a `IDLE`.

#### Nota sobre `FUERA_DE_HORARIO`
Se puede implementar de dos formas:
- **Como estado**: transición explícita a `FUERA_DE_HORARIO` al recibir mensaje fuera de horas. Ventaja: rastreable. Desventaja: hay que decidir cuándo salir de él.
- **Como condición (recomendada v1)**: no es un estado. Un middleware al inicio del handler verifica hora actual; si es fuera de horario, responde con plantilla informativa y NO llama a la FSM. La conversación queda en el estado que tenía.

Se usa la opción condición en v1.

### "Volver al paso anterior" — implementación

Cada estado define explícitamente su transición `atrás`. El botón "Volver" en Reply Buttons dispara esa transición. Estados que no la tienen: `IDLE`, `MENU_PRINCIPAL`, `EN_ASESOR_HUMANO`, `CONFIRMANDO_CANCELACION` (usa "No, regresar" en su lugar).

---

## Flujo conversacional cerrado (referencia rápida)

**Recordatorio matutino** (L-S 6:00 am, todos los clientes registrados):
> Plantilla HSM: "Buenos días {{nombre}}. ¿Deseas hacer un pedido de hielo hoy? Responde para comenzar."

**Cliente responde** → abre sesión de 24 h → transición `IDLE` → `MENU_PRINCIPAL`.

**Flujo típico de pedido** (cliente conocido, 1 producto):
1. `MENU_PRINCIPAL` → Cliente elige "Hacer pedido"
2. `SELECCIONANDO_PRODUCTO` → Cliente elige "Bolsa 5 kg"
3. `CAPTURANDO_CANTIDAD` → Cliente escribe "10"
4. `AGREGAR_MAS_O_CONTINUAR` → Cliente elige "Continuar"
5. `CAPTURANDO_DIRECCION` → Cliente elige "Usar última dirección"
6. `REVISANDO_RESUMEN` → Cliente elige "Confirmar pedido"
7. Bot envía: "Pedido #2026-0142 confirmado. Gracias." → `IDLE`

---

## Estructura del repositorio

```
automatizacion-ws-hielon/
├── claude.md                   ← este archivo
├── README.md
├── .env.example                ← variables de entorno documentadas, sin secretos
├── .gitignore
├── requirements.txt            ← o pyproject.toml si se usa Poetry
├── alembic.ini
├── alembic/
│   └── versions/               ← migraciones
├── src/
│   ├── main.py                 ← entrada FastAPI
│   ├── config.py               ← settings con Pydantic BaseSettings
│   ├── database.py             ← conexión SQLModel/asyncpg
│   ├── models/                 ← modelos SQLModel (una clase por tabla)
│   │   ├── cliente.py
│   │   ├── direccion.py
│   │   ├── producto.py
│   │   ├── pedido.py
│   │   ├── conversacion.py
│   │   └── mensaje.py
│   ├── schemas/                ← Pydantic schemas para request/response
│   ├── api/                    ← routers de FastAPI
│   │   ├── webhook.py          ← endpoint /webhook/whatsapp
│   │   ├── admin.py            ← endpoints admin (cerrar chat humano, listar pedidos)
│   │   └── health.py
│   ├── whatsapp/               ← integración con Meta Cloud API
│   │   ├── client.py           ← wrapper httpx a Cloud API
│   │   ├── signature.py        ← validación HMAC
│   │   ├── templates.py        ← definición de plantillas HSM
│   │   └── messages.py         ← helpers para construir mensajes (Reply Buttons, List, texto)
│   ├── fsm/                    ← máquina de estados
│   │   ├── states.py           ← enum de estados
│   │   ├── transitions.py      ← lógica de transición
│   │   └── handlers/           ← un handler por estado
│   ├── services/               ← lógica de negocio
│   │   ├── cliente_service.py
│   │   ├── pedido_service.py
│   │   └── locks.py            ← advisory locks por cliente_id
│   ├── notifications/          ← handoff a humano (WhatsApp a Gabriel)
│   │   └── whatsapp_admin.py
│   └── utils/
│       ├── datetime.py         ← manejo de horario laboral, TZ America/Mexico_City
│       └── logging.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_fsm_transitions.py
│   │   ├── test_signature.py
│   │   └── test_pedido_service.py
│   └── integration/
│       └── test_webhook.py
├── n8n/
│   └── workflows/              ← JSONs exportados de los flows n8n
│       └── recordatorio_matutino.json
└── docs/
    ├── setup-meta.md           ← paso a paso para dar de alta Meta Business
    ├── setup-local.md          ← cómo correr en local con ngrok
    ├── deployment.md           ← despliegue en Railway
    └── plantillas-hsm.md       ← copy y variables de cada plantilla
```

---

## Convenciones

### Python
- Formateador: **black** (line length 100).
- Linter: **ruff**.
- Type hints obligatorios en funciones públicas.
- Docstrings en formato Google.
- Nombres en `snake_case`; clases en `PascalCase`; constantes en `SCREAMING_SNAKE_CASE`.

### Git
- Rama principal: `main`.
- Rama de trabajo por issue: `feature/{issue-number}-descripcion-corta`.
- Commits en imperativo, español o inglés (consistente), max 72 chars primera línea.
- Un PR por issue, con checklist en descripción.
- Squash merge a `main`.

### Testing
- Unit tests para: FSM transitions, servicios de negocio, validación HMAC.
- Integration tests para: endpoint webhook end-to-end con mock de Meta.
- Cobertura mínima recomendada: 60% en v1, 80% después.

### Base de datos
- Toda modificación de esquema pasa por migración Alembic.
- No `.execute("ALTER TABLE ...")` manual.
- Nombres de tabla en plural y snake_case.

### Variables de entorno
- Todo secreto en `.env` (nunca commitear).
- `.env.example` con todas las variables documentadas y valores dummy.
- Cargar con Pydantic `BaseSettings`.

Variables mínimas:
```
DATABASE_URL=
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=
WHATSAPP_APP_SECRET=       ← para validar HMAC del webhook
WHATSAPP_TELEFONO_ADMIN=   ← WhatsApp personal de Gabriel, para notificar handoff
HORA_INICIO=07:00
HORA_FIN=17:00
HORA_CORTE_MISMO_DIA=14:00
TIMEZONE=America/Mexico_City

# Tarifas Meta en MXN — modelo vigente desde 1-oct-2026.
# Van en config, NO hardcodeadas: Meta las cambia y el histórico debe seguir siendo correcto.
TARIFA_SERVICE_MXN=0.1565
TARIFA_UTILITY_MXN=0.1565
TARIFA_AUTHENTICATION_MXN=0.1565
TARIFA_MARKETING_MXN=0.8000
ALERTA_GASTO_MENSUAL_MXN=2000
```

---

## Roadmap por fases (para el tablero de GitHub)

Cada fase se convierte en un **milestone**; cada bullet, en un **issue**.

### Fase 0 — Preparación administrativa (semana 1)
- [ ] Crear cuenta Meta Business para Hielon
- [ ] Verificar negocio en Meta (subir documentos)
- [ ] Adquirir/migrar número dedicado para el bot
- [ ] Crear app en developers.facebook.com
- [ ] Configurar producto WhatsApp en la app
- [ ] Generar token de acceso permanente
- [ ] Registrar plantilla `recordatorio_matutino`
- [ ] Registrar plantilla `fuera_de_horario`
- [ ] Registrar plantilla `bienvenida_opt_in`

### Fase 1 — Webhook mínimo (semana 2)
- [ ] Inicializar repo, estructura de carpetas
- [ ] `.env.example`, `requirements.txt`, README básico
- [ ] Setup FastAPI + hola mundo local
- [ ] Instalar ngrok, exponer localhost
- [ ] Endpoint `GET /webhook/whatsapp` para verificación de Meta
- [ ] Endpoint `POST /webhook/whatsapp` que loguea el body
- [ ] Configurar webhook en Meta apuntando a URL de ngrok
- [ ] Confirmar recepción de mensaje real desde celular
- [ ] Implementar validación HMAC del webhook
- [ ] Responder mensaje fijo (echo básico) llamando a Meta Cloud API

### Fase 2 — Base de datos y FSM básica (semanas 3-4)
- [ ] Instalar PostgreSQL local
- [ ] Modelar tablas con SQLModel
- [ ] Configurar Alembic, primera migración
- [ ] Crear seeds de productos (bolsa 3/5/10 kg)
- [ ] Implementar `cliente_service` (upsert por teléfono)
- [ ] Implementar guardado de mensajes entrantes con idempotencia (`message_id` único)
- [ ] Implementar FSM: enum de estados, contexto en JSONB
- [ ] Handler de `IDLE` → `MENU_PRINCIPAL`
- [ ] Handler de `MENU_PRINCIPAL` con Reply Buttons
- [ ] Advisory locks por `cliente_id` en el handler
- [ ] Testear: mensaje entra, se guarda, se envía menú, estado avanza

### Fase 3 — Flujo de pedido completo (semanas 5-6)
- [ ] Handler `SELECCIONANDO_PRODUCTO`
- [ ] Handler `CAPTURANDO_CANTIDAD` con validación de número
- [ ] Handler `AGREGAR_MAS_O_CONTINUAR` (carrito básico)
- [ ] Handler `CAPTURANDO_DIRECCION` con soporte a texto + ubicación WhatsApp
- [ ] Handler `REVISANDO_RESUMEN` con Reply Buttons
- [ ] Handler `SELECCIONANDO_MODIFICACION`
- [ ] Handler `CONFIRMANDO_CANCELACION`
- [ ] Generación de `numero_orden` legible
- [ ] Confirmación de pedido → estado `pendiente` en tabla `pedidos`
- [ ] Botón "Volver al paso anterior" en cada estado aplicable
- [ ] Middleware de horario laboral (respuesta fuera de horario)
- [ ] Mensaje "sugerimos programar para mañana" después de las 14:00

### Fase 4 — Handoff humano (semana 7)
- [ ] Handler `EN_ASESOR_HUMANO` (bot silenciado)
- [ ] Registrar plantilla `handoff_asesor` (utility) y notificar al WhatsApp de Gabriel
- [ ] Endpoint admin `POST /admin/conversaciones/{id}/cerrar-handoff`
- [ ] Botón "Hablar con asesor" en `MENU_PRINCIPAL` y `REVISANDO_RESUMEN`

### Fase 5 — Despliegue a producción (semana 8)
- [ ] Crear proyecto en Railway y conectar el repo de GitHub
- [ ] Provisionar PostgreSQL en Railway y correr las migraciones de Alembic
- [ ] Cargar variables de entorno en el panel de Railway (no hay `.env` en producción)
- [ ] Verificar el subdominio HTTPS `*.up.railway.app` (TLS automático, sin nginx ni Let's Encrypt)
- [ ] Migrar el webhook de Meta de la URL de ngrok a la de Railway
- [ ] Configurar logs estructurados
- [ ] Métricas básicas (mensajes/día, pedidos/día, errores)
- [ ] Aprender Docker fundamentos (2-3 días) — **no bloquea el despliegue**; Railway construye sin Dockerfile. Se necesita para n8n en la Fase 6 y como base para la Fase 5.1.

### Fase 5.1 — Contenerizar (opcional, después de estar en producción)
- [ ] Dockerfile del backend — solo si se quiere control explícito del build o portabilidad fuera de Railway
- [ ] docker-compose.yml para desarrollo local (Postgres + backend + n8n en una sola orden)

### Fase 6 — Recordatorios proactivos con n8n (semana 9)
- [ ] Instalar n8n vía Docker
- [ ] Flow: cron L-S 6:00 am
- [ ] Query a Postgres: clientes con opt_in y sin conversación activa hoy
- [ ] Envío de plantilla `recordatorio_matutino`
- [ ] Registro del envío en tabla de mensajes
- [ ] Manejo de errores (cliente bloqueó, límite Meta, etc.)

### Fase 3.5 — Optimización de mensajes salientes (después de Fase 3, antes de producción)

**Nota de orden (6-ago-2026)**: la instrumentación de costos estaba originalmente en la Fase 6.1, pero esta fase *arranca midiendo* el MSPC y medir exige haber instrumentado antes. El issue #79 se adelantó aquí; los endpoints y la vista se quedan en la 6.1.

- [ ] #79 — Instrumentar cada mensaje saliente con `pricing_category`, `costo_estimado` y `pedido_id`
- [ ] #80 — Medir el MSPC base del flujo implementado (línea base en `docs/mspc-baseline.md`)
- [ ] #81 — Fusionar estados que pueden viajar en un solo mensaje (ver "Presupuesto de mensajes")
- [ ] #82 — Evaluar Interactive List vs. Reply Buttons encadenados
- [ ] #83 — Atajo "repetir pedido anterior" para clientes recurrentes (**mayor ahorro esperado: -5 MSPC**)
- [ ] #84 — Política de no-respuesta a entradas irrelevantes
- [ ] #85 — Re-medir MSPC y documentar el ahorro; revertir lo que suba el abandono

**Meta de la fase**: MSPC ≤ 5 para cliente nuevo, ≤ 3 para recurrente, sin que suba la tasa de abandono.

### Fase 6.1 — Dashboard de costos propio (semana 9-10)
- [ ] #86 — Endpoint que agregue gasto por categoría y periodo (día/semana/mes)
- [ ] #87 — Endpoint de **métrica MSPC**: promedio, mediana, p90 y distribución; es el KPI de eficiencia del bot
- [ ] #88 — Costo por cliente; identificar quién consume mensajes sin comprar
- [ ] #89 — Vista HTML mínima: total por categoría, costo acumulado, proyección contra el umbral
- [ ] #90 — Alerta al WhatsApp de Gabriel si el gasto mensual estimado supera el umbral configurable

### Backlog nice-to-have (sin sprint, futuro)
- Pedido mínimo (20 bolsas)
- Programar pedido para mañana
- Detección de zona fuera de alcance por geocercas
- Panel admin React con chat en vivo (WebSockets/SSE)
- Silenciamiento por insistencia fuera de horario
- Escape hatch global "hablar con asesor" desde cualquier estado
- Modificación de items individuales dentro del carrito
- Integración con ERP
- LLM para clasificar intención y normalizar direcciones
- Multi-tenancy para Cerpomex y Fruvec

---

## Instrucciones para Claude Code

El usuario prefiere **guía paso a paso, no ejecución masiva**. Reglas:

1. **No ejecutar código sin autorización explícita**. Cada bloque de código va acompañado de una instrucción clara sobre qué hará y espera de confirmación antes de correr.
2. **Explicar los conceptos técnicos** cuando se introducen por primera vez. El usuario está aprendiendo Docker, WhatsApp API, webhooks, FSM, PostgreSQL avanzado. Asume vocabulario Python sólido y capacidad de aprender rápido, pero no des por conocidos los términos del dominio.
3. **Justificar decisiones técnicas** cuando propongas herramientas, librerías o patrones. Si hay alternativas relevantes, mencionarlas y decir por qué se elige una.
4. **Un issue a la vez.** El usuario trabaja por sprint y ticket. No brincar entre tareas.
5. **Español informal latinoamericano**. Directo, sin adulación, sin repetición innecesaria.
6. **Cuestionar decisiones del usuario cuando sean técnicamente débiles**, con fundamento. El usuario valora crítica honesta sobre validación superficial.
7. **Costo de tokens es una preocupación**. Respuestas densas, sin bullets de relleno, sin repetir contexto ya establecido en este documento.
8. **Verificar contra este documento antes de proponer alternativas al stack.** Las decisiones aquí están cerradas salvo aviso.
9. **El objetivo declarado del usuario es aprender a construir esto, no tener esto construido.** No entregar archivos terminados para que los copie. El patrón correcto por issue es: (a) explicar el problema que el archivo resuelve y por qué existe como archivo separado, (b) mostrar la forma de la solución, (c) dejar que él escriba el cuerpo, (d) revisar y corregir con fundamento. Si él pide directamente el código completo, dárselo, pero acompañado de la explicación de por qué está así.
10. **Preferir enseñar el patrón general sobre la solución particular.** Cuando aparezca algo replicable (webhook, FSM, lock, idempotencia), nombrarlo, decir dónde más se usa en la industria y qué falla si se hace mal. El usuario quiere poder repetir esto en otro proyecto.
11. **No inventar tarifas ni políticas de Meta.** Cambian seguido. Verificar contra la documentación oficial de pricing antes de afirmar un número, y actualizar la sección 2 de este documento con la fecha de verificación.
12. **Convención "COCHABAMBA" (7-ago-2026).** Cuando el usuario escriba la palabra `COCHABAMBA`, Claude entrega en el chat, solo como texto: (a) título de commit, (b) cuerpo del PR con el formato "¿Qué hace este PR?" / "Issues que cierra" / "Resultado de prueba" / "Notas", (c) el comando para crear la rama del siguiente issue. **No ejecutar** `git commit`, `git push` ni `gh pr create` al recibir este trigger — el usuario revisa y corre todo manualmente. Es su repositorio y su flujo de revisión; publicar por su cuenta le quita control sobre qué llega a `origin`.

---

## Referencias externas (leer antes de codear)

1. WhatsApp Cloud API — Getting Started: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started
2. WhatsApp Cloud API — Webhooks: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks
3. WhatsApp Cloud API — Messages: https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages
4. WhatsApp Cloud API — Message Templates: https://developers.facebook.com/docs/whatsapp/message-templates
5. FastAPI tutorial oficial: https://fastapi.tiangolo.com/tutorial/
6. SQLModel docs: https://sqlmodel.tiangolo.com/
7. Alembic tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
8. PostgreSQL advisory locks: https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS
9. n8n docs: https://docs.n8n.io/
10. LFPDPPP (México): https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf
11. **Pricing oficial de WhatsApp Business Platform** (fuente de verdad de tarifas, revisar antes de tocar la sección 2): https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing

---

## Historial de cambios de este documento

- **2026-08-06 (3)** — Sincronizados los 89 issues locales con GitHub: actualizado el body de 66 issues existentes que seguían con el contenido pre-barrido (Telegram, AWS/EC2, Caddy), y creados los 12 issues de las Fases 3.5 y 6.1 (previamente solo existían como archivo local, sin issue real en GitHub). Al crearlos, GitHub tenía el número #78 ocupado por un pull request ya mergeado, así que la numeración real quedó corrida +1: **los issues de las Fases 3.5 y 6.1 son #79-#90 en GitHub, no #78-#89.** Se renombraron los archivos en `docs/issues/` y se actualizaron sus referencias cruzadas internas y `crear-issues.sh` para reflejar la numeración real. Los 89 issues (todo salvo el PR #78) quedaron asignados al tablero del proyecto.
- **2026-08-06 (2)** — Barrido de consistencia sobre los 77 issues: handoff Telegram→WhatsApp (7 issues), despliegue AWS/EC2→Railway (8 issues, Docker degradado a Fase 5.1 opcional), pricing por mensaje de oct-2026 (6 issues), issue #10 recortado a estructura incremental. Resuelta la contradicción interna del propio CLAUDE.md (stack decía Railway, arquitectura y roadmap decían AWS). Creados 12 issues nuevos (#78-#89 en el plan original; ver entrada de arriba para la numeración real) para las Fases 3.5 y 6.1, que estaban en el roadmap sin archivos. La instrumentación de costos se movió de la Fase 6.1 a la 3.5 por dependencia circular: no se puede medir el MSPC sin haberlo instrumentado.
- **2026-08-06** — Añadidas las secciones "Estado actual y riesgos" (baneo de Meta Business, fecha objetivo oct-2026) y "Cómo se construye el repositorio" (estructura incremental, issue 10 recortado a 5 archivos). Calibrado el nivel técnico real del desarrollador y registrados los conceptos ya comprendidos para no re-explicarlos. Handoff a humano cambiado de **Telegram a WhatsApp** (Gabriel no usa Telegram): requiere plantilla `handoff_asesor` de categoría utility. Añadido el formato de 4 preguntas por archivo nuevo.
- **2026-08-05** — Reescrita la sección 2 al modelo de cobro por mensaje vigente desde el 1-oct-2026 (`service` deja de ser gratis; MX$0.1565/mensaje). Añadidas la sección 2.1 "Presupuesto de mensajes" con la métrica MSPC, la sección de alcance, la Fase 3.5 de optimización, campos `costo_estimado` y `pedido_id` en `mensajes`, y tarifas en variables de entorno. Documentada y descartada la categoría Meta Business Agent.

---

## Glosario (para consultas rápidas)

- **FSM (Finite State Machine)**: máquina de estados finita. Modelo formal de un sistema con estados discretos y transiciones definidas.
- **HSM (Highly Structured Message)**: plantilla de mensaje pre-aprobada por Meta, usada fuera de la ventana de sesión de 24h.
- **Webhook**: endpoint HTTP que recibe notificaciones push de otro sistema (aquí, Meta).
- **Idempotencia**: propiedad de una operación que puede repetirse sin efecto adicional. Necesaria porque Meta puede reintentar entregar el mismo webhook.
- **HMAC-SHA256**: algoritmo de firma criptográfica que Meta usa para probar que un webhook viene de ellos.
- **Race condition**: bug que ocurre cuando dos operaciones concurrentes acceden a un mismo recurso sin coordinación.
- **Advisory lock (PostgreSQL)**: mecanismo de bloqueo cooperativo por clave arbitraria (aquí, cliente_id) para serializar el procesamiento de mensajes de un mismo cliente.
- **BSP (Business Solution Provider)**: proveedor certificado por Meta que revende acceso al API con features adicionales (Twilio, 360dialog, etc.). En este proyecto NO se usa BSP; se integra directo con Cloud API.
- **Opt-in**: consentimiento explícito del cliente para recibir mensajes proactivos. Obligatorio por LFPDPPP y política Meta. El opt-in para marketing es adicional y separado del opt-in básico.
- **Pricing category**: clasificación (`service`, `utility`, `marketing`, `authentication`, `Meta Business Agent`) que Meta asigna a cada mensaje saliente y reporta vía webhook; base para el dashboard de costos propio del proyecto.
- **MSPC (mensajes salientes por pedido completado)**: métrica propia del proyecto. Cuántos mensajes cobrables gasta el bot para cerrar un pedido. Es la unidad económica del sistema desde el cambio de tarifas del 1-oct-2026.
- **Meta Business Agent**: quinta categoría de mensaje (agosto 2026). Meta procesa el mensaje del cliente con su propio LLM y genera la respuesta; cobra por tokens de procesamiento más el envío. Descartada en este proyecto.
- **Ventana de sesión de 24h**: periodo que se abre cuando el cliente escribe, durante el cual el negocio puede responder con texto libre en vez de plantilla. Desde el 1-oct-2026 sigue determinando *qué formato* se puede enviar, pero ya **no** determina si el mensaje es gratis.
- **Ventana rodante (rolling window)**: el límite de conversaciones iniciadas por el negocio (250, 1000, etc.) no se reinicia a medianoche — se calcula sobre cualquier periodo de 24h hacia atrás desde el momento actual.