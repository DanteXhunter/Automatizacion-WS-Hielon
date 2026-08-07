## Depende de

- #79 — mensajes instrumentados con categoría y costo

## Objetivo

Un endpoint que responda cuánto se ha gastado, por categoría y por periodo.

## Endpoint

```
GET /admin/costos?desde=2026-10-01&hasta=2026-10-31&agrupar=dia
```

```json
{
  "periodo": {"desde": "2026-10-01", "hasta": "2026-10-31"},
  "total_mxn": 1352.40,
  "por_categoria": {
    "service": {"mensajes": 7200, "costo_mxn": 1126.80},
    "utility": {"mensajes": 1440, "costo_mxn": 225.36},
    "marketing": {"mensajes": 0, "costo_mxn": 0}
  },
  "serie": [{"fecha": "2026-10-01", "mensajes": 280, "costo_mxn": 43.82}]
}
```

## De dónde sale el costo

De `mensajes.costo_estimado`, **sumando el snapshot guardado**, nunca
recalculando con la tarifa actual. Si Meta sube el precio a mitad de mes, el
reporte debe seguir mostrando lo que de verdad se pagó cada día.

## Por qué "estimado" y no "real"

Meta factura con sus propios cortes y su propio tipo de cambio USD→MXN. Este
número sirve para **detectar desviaciones y tendencias**, no para conciliar
contabilidad. Dejarlo explícito en la respuesta o en la documentación del
endpoint, para que nadie lo use como cifra fiscal.

## Autenticación

Este endpoint expone información financiera del negocio. En v1 no hay login (el
panel es otro proyecto), así que se protege con un **API key en header**,
distinto del token de Meta. Un endpoint de costos abierto en internet es una
fuga de información de negocio.

## Criterio de aceptación

- [ ] Responde totales por categoría y serie temporal
- [ ] Agrupación por día, semana y mes
- [ ] Suma `costo_estimado`, no recalcula tarifas
- [ ] Protegido con API key
- [ ] Visible y probable desde Swagger (`/docs`)
