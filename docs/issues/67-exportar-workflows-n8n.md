## Depende de

- #62 a #66 — el flow terminado que se exporta

## Objetivo

Versionar la automatización igual que el resto del código.

## Contexto

Los flows de n8n viven en su base de datos interna. Sin exportarlos, todo el
trabajo de las Fases 6 solo existe dentro del contenedor de n8n: no hay
historial de cambios, no hay forma de revisar qué se modificó, y una pérdida
del volumen de n8n se lleva la automatización completa sin rastro.

## Cómo exportar

Desde la UI de n8n: cada workflow tiene la opción "Download" que genera un
JSON. Guardarlos en:

```
n8n/workflows/recordatorio_matutino.json
```

## Antes de commitear: quitar credenciales

n8n permite exportar workflows con las credenciales embebidas si no se
configura bien. Revisar el JSON exportado y confirmar que las credenciales de
Postgres y de Meta **no** quedan en texto plano dentro
del archivo. n8n normalmente las referencia por ID de credencial guardada
aparte en su propia base, no en el JSON del workflow; verificar que sea así
antes de subirlo.

## Mantenimiento

Cada vez que se modifique un flow en la UI de producción, reexportar y
commitear el JSON actualizado. Si esto se vuelve tedioso, considerar la CLI de
n8n para exportar en automático como parte del runbook de despliegue (issue
#60).

## Criterio de aceptación

- [ ] `n8n/workflows/recordatorio_matutino.json` existe y está commiteado
- [ ] Revisado manualmente que no contiene ninguna credencial en texto plano
- [ ] Documentado el paso de exportar como parte del checklist de cualquier
      cambio futuro al flow
