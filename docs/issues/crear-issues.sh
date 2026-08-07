#!/usr/bin/env bash
# Crea los issues del proyecto en GitHub, uno por comando, leyendo el body
# desde su archivo .md correspondiente en docs/issues/.
#
# Uso:
#   cd docs/issues
#   bash crear-issues.sh              # crea todos
#   bash crear-issues.sh 34 46        # crea solo el rango de issues 34 a 46
#
# Revisa cada bloque antes de correr. gh pide confirmación implícita al
# imprimir la URL creada; si algo sale mal, el issue creado se borra o
# edita a mano desde GitHub.
#
# Nota (6-ago-2026): el número de issue creado por gh NO siempre coincide
# con el número usado aquí abajo — GitHub numera issues y PRs en la misma
# secuencia. El #78 quedó ocupado por un PR merged, así que los issues que
# originalmente iban del 78 al 89 se corrieron al 79-90 (ya creados y
# renombrados en docs/issues/ para que el número del archivo coincida con
# el número real en GitHub). Si vuelves a correr este script en un repo
# limpio, verifica el número real que devuelve `gh issue create` en vez de
# asumir que coincide con el de esta lista.

set -euo pipefail
cd "$(dirname "$0")"

DESDE="${1:-1}"
HASTA="${2:-90}"

crear() {
  local numero="$1" titulo="$2" labels="$3" milestone="$4" archivo="$5"
  if (( numero < DESDE || numero > HASTA )); then return; fi
  echo "==> Creando issue #${numero}: ${titulo}"
  if [ -n "$milestone" ]; then
    gh issue create --title "$titulo" --label "$labels" --milestone "$milestone" --body-file "$archivo"
  else
    gh issue create --title "$titulo" --label "$labels" --body-file "$archivo"
  fi
  sleep 1
}

M0="Fase 0 - Preparacion administrativa"
M1="Fase 1 - Webhook minimo"
M2="Fase 2 - Base de datos y FSM basica"
M3="Fase 3 - Flujo de pedido completo"
M4="Fase 4 - Handoff humano"
M5="Fase 5 - Despliegue a produccion"
M6="Fase 6 - Recordatorios proactivos"
M35="Fase 3.5 - Optimizacion de mensajes salientes"
M61="Fase 6.1 - Dashboard de costos"

# --- Fase 0 ---
crear 1  "Crear cuenta de Meta Business para Hielon"                  "setup,meta-api,legal"        "$M0" "01-crear-cuenta-meta-business.md"
crear 2  "Verificar el negocio en Meta con documentacion fiscal"      "setup,meta-api,legal"        "$M0" "02-verificar-negocio-meta.md"
crear 3  "Adquirir o migrar el numero dedicado del bot"               "setup,meta-api"              "$M0" "03-numero-dedicado.md"
crear 4  "Crear app en developers.facebook.com"                       "setup,meta-api"              "$M0" "04-crear-app-meta.md"
crear 5  "Configurar producto WhatsApp y vincular el numero"          "setup,meta-api"              "$M0" "05-configurar-producto-whatsapp.md"
crear 6  "Generar token de acceso permanente con System User"         "setup,meta-api,seguridad"    "$M0" "06-token-permanente.md"
crear 7  "Registrar plantilla HSM recordatorio_matutino"              "meta-api,legal"              "$M0" "07-plantilla-recordatorio-matutino.md"
crear 8  "Registrar plantillas fuera_de_horario y bienvenida_opt_in"  "meta-api,legal"              "$M0" "08-plantillas-horario-y-optin.md"
crear 9  "Redactar aviso de privacidad y mecanismo de opt-in"         "legal,docs"                  "$M0" "09-aviso-privacidad-optin.md"

# --- Fase 1 ---
crear 10 "Inicializar estructura de carpetas del proyecto"            "setup,backend"               "$M1" "10-estructura-carpetas.md"
crear 11 "Configurar requirements, .gitignore y .env.example"         "setup,docs"                  "$M1" "11-requirements-gitignore-env.md"
crear 12 "Levantar FastAPI con endpoint de health"                    "backend"                     "$M1" "12-fastapi-health.md"
crear 13 "Implementar config.py con Pydantic BaseSettings"            "backend,seguridad"           "$M1" "13-config-basesettings.md"
crear 14 "Instalar ngrok y exponer localhost"                         "infra"                       "$M1" "14-ngrok.md"
crear 15 "Endpoint GET /webhook/whatsapp para verificacion de Meta"   "backend,meta-api"            "$M1" "15-webhook-get-verificacion.md"
crear 16 "Endpoint POST /webhook/whatsapp que loguea el payload"      "backend,meta-api"            "$M1" "16-webhook-post-log.md"
crear 17 "Configurar el webhook en Meta y confirmar mensaje real"     "meta-api,infra"              "$M1" "17-configurar-webhook-meta.md"
crear 18 "Validar la firma HMAC-SHA256 del webhook"                   "backend,meta-api,seguridad"  "$M1" "18-validar-hmac.md"
crear 19 "Cliente httpx para Meta Cloud API y respuesta echo"         "backend,meta-api"            "$M1" "19-cliente-httpx-echo.md"
crear 20 "Tests unitarios de validacion de firma HMAC"                "testing,seguridad"           "$M1" "20-tests-hmac.md"

# --- Fase 2 ---
crear 21 "Instalar PostgreSQL local y crear la base"                  "db,infra"                    "$M2" "21-postgres-local.md"
crear 22 "Modelar las 7 tablas con SQLModel"                          "db,backend"                  "$M2" "22-modelar-tablas-sqlmodel.md"
crear 23 "Configurar Alembic y generar la migracion inicial"          "db"                          "$M2" "23-alembic-migracion-inicial.md"
crear 24 "Seed de productos: bolsas de 3, 5 y 10 kg"                  "db"                          "$M2" "24-seed-productos.md"
crear 25 "Implementar cliente_service con upsert por telefono"        "backend"                     "$M2" "25-cliente-service-upsert.md"
crear 26 "Persistir mensajes entrantes con idempotencia"              "backend,db"                  "$M2" "26-idempotencia-mensajes.md"
crear 27 "Definir el enum de estados de la FSM"                       "fsm,backend"                 "$M2" "27-enum-estados-fsm.md"
crear 28 "Implementar el dispatcher de transiciones"                  "fsm,backend"                 "$M2" "28-dispatcher-transiciones.md"
crear 29 "Handler IDLE con saludo y menu principal"                   "fsm"                         "$M2" "29-handler-idle.md"
crear 30 "Handler MENU_PRINCIPAL con Reply Buttons"                   "fsm,meta-api"                "$M2" "30-handler-menu-principal.md"
crear 31 "Advisory locks de PostgreSQL por cliente_id"                "backend,db,seguridad"        "$M2" "31-advisory-locks.md"
crear 32 "Utilidades de horario laboral con timezone"                 "backend"                     "$M2" "32-utils-horario.md"
crear 33 "Test de integracion del flujo mensaje a menu"               "testing"                     "$M2" "33-test-integracion-mensaje-menu.md"

# --- Fase 3 ---
crear 34 "Handler SELECCIONANDO_PRODUCTO"                             "fsm"                         "$M3" "34-handler-seleccionando-producto.md"
crear 35 "Handler CAPTURANDO_CANTIDAD con validacion estricta"        "fsm,backend"                 "$M3" "35-handler-capturando-cantidad.md"
crear 36 "Handler AGREGAR_MAS_O_CONTINUAR con carrito"                "fsm"                         "$M3" "36-handler-agregar-mas-o-continuar.md"
crear 37 "Handler CAPTURANDO_DIRECCION con texto y ubicacion"         "fsm,meta-api"                "$M3" "37-handler-capturando-direccion.md"
crear 38 "Handler REVISANDO_RESUMEN"                                  "fsm"                         "$M3" "38-handler-revisando-resumen.md"
crear 39 "Handler SELECCIONANDO_MODIFICACION"                         "fsm"                         "$M3" "39-handler-seleccionando-modificacion.md"
crear 40 "Handler CONFIRMANDO_CANCELACION"                            "fsm"                         "$M3" "40-handler-confirmando-cancelacion.md"
crear 41 "Generacion de numero_orden legible y sin colisiones"        "backend,db"                  "$M3" "41-numero-orden.md"
crear 42 "Confirmacion de pedido en una transaccion atomica"          "backend,db"                  "$M3" "42-confirmacion-pedido-transaccion.md"
crear 43 "Validador de transiciones de estado del pedido"             "backend,testing"             "$M3" "43-validador-transiciones-pedido.md"
crear 44 "Boton Volver transversal en los estados aplicables"         "fsm"                         "$M3" "44-boton-volver.md"
crear 45 "Middleware de horario laboral"                              "backend,fsm"                 "$M3" "45-middleware-horario.md"
crear 46 "Sugerencia de programar para manana despues de las 14:00"   "backend,fsm"                 "$M3" "46-sugerencia-programar-manana.md"

# --- Fase 4 ---
crear 47 "Handler EN_ASESOR_HUMANO con bot silenciado"                "fsm,admin"                   "$M4" "47-handler-en-asesor-humano.md"
crear 48 "Notificacion de handoff por WhatsApp a Gabriel"             "admin,backend"               "$M4" "48-notificacion-whatsapp-admin.md"
crear 49 "Endpoint admin para cerrar el handoff"                      "admin,backend,seguridad"     "$M4" "49-endpoint-cerrar-handoff.md"
crear 50 "Boton Hablar con asesor en menu y resumen"                  "fsm"                         "$M4" "50-boton-hablar-asesor.md"
crear 51 "Endpoints admin de consulta de pedidos"                     "admin,backend"               "$M4" "51-endpoints-admin-pedidos.md"

# --- Fase 5 ---
crear 52 "Aprender fundamentos de Docker"                             "docs,devops"                 "$M5" "52-aprender-docker.md"
crear 53 "Dockerfile del backend"                                     "devops"                      "$M5" "53-dockerfile-backend.md"
crear 54 "docker-compose con Postgres, backend y n8n"                 "devops"                      "$M5" "54-docker-compose.md"
crear 55 "Provisionar el proyecto en Railway"                         "devops"                      "$M5" "55-provisionar-railway.md"
crear 56 "HTTPS con el subdominio de Railway"                         "devops,seguridad"            "$M5" "56-https-subdominio-railway.md"
crear 57 "Migrar el webhook de ngrok al dominio real"                 "meta-api,devops"             "$M5" "57-migrar-webhook-produccion.md"
crear 58 "Logs estructurados en JSON"                                 "devops,backend"              "$M5" "58-logs-estructurados.md"
crear 59 "Metricas basicas de operacion"                              "devops,backend"              "$M5" "59-metricas-basicas.md"
crear 60 "Runbook de despliegue y respaldos"                          "docs,devops"                 "$M5" "60-runbook-despliegue.md"

# --- Fase 6 ---
crear 61 "Instalar n8n en Railway"                                    "n8n,devops"                  "$M6" "61-instalar-n8n.md"
crear 62 "Flow con cron lunes a sabado a las 6:00"                    "n8n"                         "$M6" "62-flow-cron-6am.md"
crear 63 "Query de clientes elegibles para recordatorio"              "n8n,db,legal"                "$M6" "63-query-clientes-elegibles.md"
crear 64 "Envio de la plantilla recordatorio_matutino"                "n8n,meta-api"                "$M6" "64-envio-plantilla-recordatorio.md"
crear 65 "Registrar los envios salientes en la tabla mensajes"        "n8n,db"                      "$M6" "65-registrar-envios-mensajes.md"
crear 66 "Manejo de errores del envio masivo"                         "n8n"                         "$M6" "66-manejo-errores-envio-masivo.md"
crear 67 "Exportar los workflows de n8n al repositorio"               "n8n,docs"                    "$M6" "67-exportar-workflows-n8n.md"

# --- Backlog (sin milestone) ---
crear 68 "Regla de pedido minimo de 20 bolsas"                        "backlog,fsm"                 ""    "68-pedido-minimo.md"
crear 69 "Programar pedidos para dias futuros"                        "backlog,fsm"                 ""    "69-programar-pedidos-futuros.md"
crear 70 "Deteccion de zona fuera de cobertura por geocercas"         "backlog,backend"             ""    "70-geocercas-cobertura.md"
crear 71 "Panel admin con chat en vivo"                               "backlog"                     ""    "71-panel-admin-chat-vivo.md"
crear 72 "Escape hatch global hacia asesor humano"                    "backlog,fsm"                 ""    "72-escape-hatch-global.md"
crear 73 "Edicion de items individuales del carrito"                  "backlog,fsm"                 ""    "73-edicion-items-individuales.md"
crear 74 "Silenciamiento por insistencia fuera de horario"            "backlog,backend"             ""    "74-silenciamiento-fuera-horario.md"
crear 75 "Multi-tenancy para Cerpomex y Fruvec"                       "backlog,db"                  ""    "75-multitenancy-grupo.md"
crear 76 "Integracion con el ERP interno"                             "backlog,backend"             ""    "76-integracion-erp.md"
crear 77 "Clasificacion de intencion con LLM"                         "backlog,backend"             ""    "77-llm-clasificacion-intencion.md"

# --- Fase 3.5 (va despues de la Fase 3, antes de produccion) ---
crear 79 "Instrumentar costo y categoria de cada mensaje saliente"    "backend,costos,db"           "$M35" "79-instrumentar-costos-mensajes.md"
crear 80 "Medir el MSPC base del flujo actual"                       "backend,costos"              "$M35" "80-medir-mspc-base.md"
crear 81 "Fusionar estados que caben en un solo mensaje"             "fsm,costos"                  "$M35" "81-fusionar-estados-mensajes.md"
crear 82 "Evaluar Interactive List contra Reply Buttons"             "fsm,costos"                  "$M35" "82-interactive-list-vs-buttons.md"
crear 83 "Atajo repetir pedido anterior para recurrentes"            "fsm,costos"                  "$M35" "83-atajo-repetir-pedido-anterior.md"
crear 84 "Politica de no respuesta a entradas irrelevantes"          "fsm,costos"                  "$M35" "84-politica-no-respuesta.md"
crear 85 "Re-medir MSPC y documentar el ahorro"                      "backend,costos,docs"         "$M35" "85-remedir-mspc-documentar-ahorro.md"

# --- Fase 6.1 ---
crear 86 "Endpoint de gasto por categoria y periodo"                 "backend,costos,admin"        "$M61" "86-endpoint-gasto-por-categoria.md"
crear 87 "Endpoint de metrica MSPC"                                  "backend,costos,admin"        "$M61" "87-endpoint-metrica-mspc.md"
crear 88 "Costo por cliente y deteccion de gasto sin venta"          "backend,costos,admin"        "$M61" "88-costo-por-cliente.md"
crear 89 "Vista HTML del dashboard de costos"                        "backend,costos,admin"        "$M61" "89-vista-dashboard-costos.md"
crear 90 "Alerta de gasto mensual al WhatsApp de Gabriel"            "backend,costos,alertas"      "$M61" "90-alerta-gasto-mensual.md"

echo "Listo. Verifica con: gh issue list --limit 100"
