## Idea de backlog

Exponer o empujar los pedidos confirmados hacia el ERP interno del grupo, que
es el destino final de los datos capturados por este bot, según el objetivo
general del proyecto en `claude.md`.

## Alcance futuro

- Definir si la integración es el ERP consultando una API de este sistema, o
  este sistema empujando eventos hacia el ERP (webhook saliente, cola, o
  sincronización periódica vía n8n)
- Mapeo de campos entre el modelo de datos de este proyecto y el del ERP
- Manejo de fallos de sincronización sin perder pedidos

## Por qué no en v1

El ERP está explícitamente fuera del alcance de este proyecto y, hasta donde
se documenta aquí, ni siquiera está construido todavía. No hay con qué
integrar.
