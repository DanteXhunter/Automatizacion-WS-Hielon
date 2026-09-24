# Reglas de trabajo del proyecto

Este archivo registra las correcciones y decisiones de trabajo indicadas por el propietario del proyecto. Debe consultarse **antes de modificar código, recomendar una dirección técnica o preparar instrucciones de Git, commits o pull requests**.

Si una respuesta o acción planeada contradice estas reglas, debe corregirse antes de continuar. Cada nueva corrección del propietario se agrega a este documento sin borrar las anteriores, salvo que él sustituya explícitamente una decisión.

## Responsabilidades

- Codex se encarga del análisis, la implementación, las pruebas y la explicación técnica.
- El propietario ejecuta los commits, los pushes y la creación o edición de pull requests.
- Codex nunca debe ejecutar `git commit`, `git push` ni crear un pull request.
- Ningún commit, pull request, archivo o comentario debe atribuir autoría, mérito o contribución a Codex, OpenAI o cualquier otra IA.
- No se deben solicitar al propietario acciones que Codex pueda resolver técnicamente dentro del repositorio.
- Nunca se debe leer, mostrar ni registrar el contenido de `.env`.

## Ritmo de trabajo e issues

- La unidad predeterminada de entrega es un bloque de cinco issues.
- El tamaño del bloque puede reducirse si los issues son grandes o aumentarse si son pequeños.
- Si el propietario puede avanzar en paralelo con una configuración externa
  independiente, Codex debe darle las instrucciones necesarias y continuar el
  bloque técnico en el repositorio durante el mismo turno.
- Antes de comenzar otro bloque, separar y entregar cualquier cambio pendiente
  del bloque anterior para no acumular trabajo sin commit ni mezclar alcances.
- Antes de empezar un archivo nuevo se debe poder responder:
  1. ¿Qué va a contener?
  2. ¿Dónde vive y por qué ahí?
  3. ¿Por qué se le asignó ese nombre?
  4. ¿Por qué se crea en esta etapa y no antes o después?
- No se considera terminado un bloque hasta verificar el comportamiento con pruebas proporcionales al cambio.
- No se debe afirmar que un issue quedó resuelto si su criterio de aceptación no está implementado y comprobado.

## Comandos de Git

- Entregar únicamente los comandos necesarios para la operación solicitada.
- Para comprobar el resultado basta con `git status`, salvo que exista una razón técnica concreta para pedir otra validación.
- Evitar cadenas de verificaciones redundantes como `git diff --cached --check`, `git diff --cached --stat` y `git status --short` cuando el propietario solo necesita confirmar el estado.
- No incluir comandos para crear o editar el pull request: esa parte se realiza directamente en GitHub.
- No incluir `AGENTS.md` ni `graphify-out/` en staging, commits o instrucciones de entrega.
- No mezclar accidentalmente cambios de bloques de issues distintos.

## Commits

- Mantener un commit coherente por cada bloque acordado de cinco issues, salvo
  que el tamaño del trabajo justifique otra división.
- El título debe ser breve, específico y describir el resultado implementado.
- El cuerpo debe:
  - resumir el trabajo realizado;
  - enumerar los issues incluidos;
  - usar `Closes #N` únicamente para issues realmente terminados;
  - indicar cuáles serán los siguientes issues.
- No usar mensajes vagos ni cuerpos que solo repitan el título.

## Pull requests

### Título predeterminado

- Escribirlo en español.
- Usar estilo oración y una redacción funcional, clara y específica.
- No copiar automáticamente el título técnico del commit.
- No usar un prefijo en inglés como `feat:` si perjudica la presentación.
- Ejemplo de estilo: `Implementar captura de dirección, revisión y cancelación del pedido`.

### Cuerpo predeterminado

Entregarlo como Markdown sin renderizar, dentro de un bloque `markdown` listo para copiar en GitHub. Debe respetar esta estructura:

```markdown
## Resumen

Explicación breve del objetivo y del resultado funcional del PR.

## Cambios realizados

### Área funcional

- Cambio concreto y comprensible.
- Cambio concreto y comprensible.

## Validación

- Resultado de las pruebas ejecutadas.
- Resultado de las herramientas de calidad aplicables.

## Issues resueltos

- Closes #N
- Closes #N

## Próximos issues

- [#N — Nombre del siguiente trabajo](URL_DEL_ISSUE)
```

Reglas editoriales del cuerpo:

- Usar encabezados, espacios en blanco y listas para crear una jerarquía visual clara.
- Escribir con ortografía, puntuación y concordancia correctas.
- Describir resultados funcionales antes que nombres internos de clases, archivos o handlers.
- Evitar párrafos amontonados, texto plano sin secciones y listas sin contexto.
- Explicar qué cambió, por qué importa y cómo se validó.
- Incluir enlaces Markdown en los próximos issues.
- Usar cada cierre `Closes #N` en una línea separada.
- No afirmar que GitHub cerrará automáticamente un issue si el destino del PR no cumple las condiciones de cierre de la plataforma.

## README

- El README es documentación general y permanente del proyecto.
- No debe mencionar ramas, bloques de issues, números de issues ni detalles temporales de un pull request.
- Debe ser profesional, legible y útil para comprender, instalar, configurar, probar y ejecutar el sistema.
- Debe priorizar información práctica y mover explicaciones extensas a documentación especializada.

## Comunicación y criterio

- Responder en español claro, directo y sin redundancia.
- Explicar primero el resultado y después los detalles técnicos necesarios.
- Al hablar del estado del proyecto, traducir el código a capacidades reales del negocio: qué puede hacer hoy, qué no puede hacer y cómo se usará.
- Inferir y aplicar buenas prácticas evidentes sin obligar al propietario a especificar cada detalle.
- Si una afirmación depende de información externa cambiante, comprobarla antes de presentarla como un hecho.

## Prioridades funcionales y operación del negocio

- La prioridad es completar el núcleo operativo antes de desarrollar el panel web.
- El orden obligatorio es:
  1. permitir que el cliente complete un pedido;
  2. confirmar y persistir el pedido de forma consistente;
  3. guardar el historial completo de la conversación;
  4. consultar conversaciones y pedidos mediante endpoints administrativos;
  5. realizar el handoff y devolver el control al bot;
  6. desplegar y validar el circuito con Meta;
  7. desarrollar el panel web sencillo al final.
- La operación humana usará WhatsApp Business mediante **Coexistence** con Cloud API, sujeto a comprobar que la cuenta y el número sean elegibles antes de registrarlos o migrarlos.
- El handoff se controla **por conversación y por cliente**, nunca de forma global.
  Mientras una conversación esté en handoff, el bot permanece silenciado solo
  para ese cliente; debe continuar atendiendo normalmente a todos los demás.
- El asesor responderá desde WhatsApp Business mediante Coexistence.
- El panel web sencillo complementará la operación: mostrará pedidos, conversaciones, historial y estado del handoff. No sustituirá el punto de venta.
- **My Business POS 2011** seguirá siendo el sistema administrativo y punto de venta de Hielon.
- En el MVP, la secretaria consulta el pedido confirmado, lo captura manualmente
  en My Business POS 2011 y desde ahí imprime el ticket.
- No se debe convertir este proyecto en un ERP, inventario o punto de venta paralelo.
- Cualquier automatización futura de My Business POS 2011 debe comenzar con una
  investigación técnica de la instalación real y de los mecanismos soportados
  por el fabricante. No se debe asumir una API moderna, escribir directamente
  en su base de datos ni automatizar su interfaz sin probar seguridad,
  idempotencia y recuperación ante fallos.
