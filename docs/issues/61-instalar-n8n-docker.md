## Depende de

- #54 — n8n ya declarado en el compose
- #56 — reverse proxy para el subdominio

## Objetivo

Tener n8n operativo como motor de las automatizaciones proactivas.

## Contexto

n8n es la herramienta que dispara el cron matutino y en el futuro sincronizará
con el ERP. Ya quedó agregado al `docker-compose.yml` en el issue #54; este
issue es dejarlo realmente utilizable.

## Configuración

- Detrás del reverse proxy de Caddy, en un subdominio propio:
  `n8n.hielondeleon.com`
- Protegido con autenticación básica (usuario y contraseña), variables
  `N8N_BASIC_AUTH_USER` y `N8N_BASIC_AUTH_PASSWORD` en el `.env`
- Volumen persistente ya declarado (`n8n_data`) para no perder los flows al
  recrear el contenedor
- Timezone del contenedor en `America/Mexico_City` vía la variable
  `GENERIC_TIMEZONE`; por defecto n8n corre en UTC y el cron del issue #62
  saldría mal si no se fija esto aquí

## Por qué no correr n8n en la misma instancia sin aislarlo

Ya está en Docker Compose junto a Postgres y el backend, así que el
aislamiento de procesos ya existe. Lo que falta es que no quede expuesto sin
autenticación: n8n con acceso libre permite a cualquiera crear workflows que
toquen la misma base de datos.

## Criterio de aceptación

- [ ] n8n accesible en su subdominio con HTTPS
- [ ] Pide usuario y contraseña antes de mostrar cualquier flow
- [ ] Timezone del contenedor confirmado en America/Mexico_City
- [ ] Un flow de prueba sobrevive a un `docker compose restart`
