## Depende de

- #55 — proyecto de Railway donde se agrega n8n

## Objetivo

Tener n8n operativo como motor de las automatizaciones proactivas.

## Contexto

n8n es la herramienta que dispara el cron matutino y en el futuro sincronizará
con el ERP. Se despliega como un servicio más del proyecto de Railway, con su propio
subdominio y su propio volumen.

## Configuración

- Desplegar con el template oficial de n8n de Railway (**New > Template >
  n8n**), en el mismo proyecto que el backend
- Generar su propio subdominio `*.up.railway.app`, distinto al del backend
- Protegido con autenticación básica, variables `N8N_BASIC_AUTH_ACTIVE=true`,
  `N8N_BASIC_AUTH_USER` y `N8N_BASIC_AUTH_PASSWORD` en Variables
- **Volumen persistente montado en `/home/node/.n8n`**: sin él, cada redeploy
  borra todos los flows. El template lo trae; verificar que exista.
- Timezone del contenedor en `America/Mexico_City` vía la variable
  `GENERIC_TIMEZONE`; por defecto n8n corre en UTC y el cron del issue #62
  saldría mal si no se fija esto aquí

## Por qué autenticación no es opcional

El subdominio de n8n es público. **n8n sin autenticación permite a cualquiera
crear workflows que toquen la misma base de datos de producción**, incluida la
tabla de clientes. Es el riesgo más grande de esta fase y se cierra con dos
variables de entorno.

n8n corre como servicio aparte, no dentro del backend: si un flow se atora o
consume memoria, no tumba el webhook.

## Criterio de aceptación

- [ ] n8n accesible en su propio subdominio de Railway con HTTPS
- [ ] Pide usuario y contraseña antes de mostrar cualquier flow
- [ ] Timezone del contenedor confirmado en America/Mexico_City
- [ ] Un flow de prueba sobrevive a un redeploy del servicio
