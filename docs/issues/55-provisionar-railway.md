## Depende de

Nada del código. Solo requiere cuenta de Railway y el repo en GitHub.

## Objetivo

Levantar el backend y la base de datos de producción en Railway.

## Por qué Railway y no AWS EC2 (decisión revisada 6-ago-2026)

Este issue originalmente provisionaba una instancia EC2 con Docker, security
groups, IP elástica y Caddy para el TLS. Se cambió porque **es
desproporcionado para el volumen del proyecto** (30-50 pedidos/día) y le mete
al desarrollador cuatro tecnologías nuevas antes de poder desplegar nada.

Lo que Railway resuelve solo, y que en EC2 eran issues aparte:

| En EC2 había que | En Railway |
|---|---|
| Provisionar instancia, elegir AMI, IP elástica | Crear proyecto y conectar el repo |
| Instalar Docker y Docker Compose | No hace falta; construye desde el repo |
| Configurar security groups | Solo se expone el puerto HTTP del servicio |
| Instalar y configurar Postgres | Un servicio de la plataforma, con backups |
| Caddy + Let's Encrypt para HTTPS | Subdominio con TLS automático |
| Copiar el código por `scp` o montar CI | Deploy automático en cada push |

El trade-off aceptado: menos control y dependencia de un proveedor. A este
volumen, no importa. Si algún día importa, el Dockerfile de la Fase 5.1
permite migrar a cualquier lado.

## Pasos

1. Crear cuenta en Railway y un proyecto nuevo
2. **New > GitHub Repo**, seleccionar el repo del bot
3. Railway detecta Python y el `requirements.txt`, e instala solo
4. **New > Database > PostgreSQL** dentro del mismo proyecto
5. Definir el start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
6. Cargar las variables de entorno en **Variables** (ver más abajo)
7. **Settings > Networking > Generate Domain** para obtener el subdominio

## Variables de entorno

**En producción no hay `.env`.** Se pegan en el panel de Railway, que las
inyecta al entorno del proceso. Son las mismas del `.env.example` del issue
#11, con dos diferencias:

- `DATABASE_URL` no se escribe a mano: se referencia la del servicio de
  Postgres con `${{Postgres.DATABASE_URL}}`
- `PORT` la define Railway; el start command debe usarla, no un puerto fijo

## Detalle que rompe el deploy si se ignora

Uvicorn debe escuchar en `0.0.0.0`, no en `127.0.0.1`. Con `127.0.0.1` el
proceso arranca bien, los logs se ven sanos, y el servicio es inalcanzable
desde fuera del contenedor. Es el error más común al desplegar por primera vez.

## Migraciones

Las de Alembic (issue #23) se corren contra la base de Railway antes del
primer arranque real. Se puede hacer desde local apuntando `DATABASE_URL` a la
URL pública de Postgres de Railway, o agregando `alembic upgrade head` al
comando de arranque.

## Criterio de aceptación

- [ ] Servicio desplegado y con estado *Active* en Railway
- [ ] PostgreSQL provisionado en el mismo proyecto y alcanzable por el backend
- [ ] Todas las variables cargadas; el arranque no falla por config faltante
- [ ] Migraciones de Alembic aplicadas contra la base de producción
- [ ] Un `git push` a `main` dispara un redeploy automático
