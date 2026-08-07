## Depende de

- #86, #87, #88 — los tres endpoints

## Objetivo

Una página que Gabriel pueda abrir sin saber qué es un JSON.

## Alcance deliberadamente mínimo

**Una sola página HTML servida por FastAPI.** Sin React, sin build, sin
frontend aparte. El panel de verdad es otro proyecto (issue #71); esto es un
reporte de lectura.

Si esto se convierte en un frontend, se está construyendo el proyecto
equivocado y ninguno de los dos se termina.

## Contenido

```
GASTO DE MENSAJERIA - Octubre 2026

Total del mes:        MX$ 1,352.40
Proyeccion a fin:     MX$ 1,610.00     (umbral: MX$ 2,000)

Por categoria
  service    7,200 msj    MX$ 1,126.80
  utility    1,440 msj    MX$   225.36

Eficiencia
  Pedidos completados         812
  MSPC promedio               4.7
  Costo por pedido      MX$  0.74
  Gasto sin pedido      MX$ 286.40   (21% del total)

[grafica de barras: gasto diario del mes]
```

## Detalles que la hacen útil

- **Proyección a fin de mes**: el dato accionable es "vas a gastar X", no
  "llevas Y". Lineal sobre los días transcurridos alcanza.
- **El porcentaje de gasto sin pedido** es el número que dispara acción.
- **Comparación contra el mes anterior**, para ver tendencia.

## Implementación

Jinja2 (ya viene con FastAPI vía `fastapi.templating`) más una tabla HTML. La
gráfica, con SVG generado en el servidor o barras de CSS. **Sin librerías de
JavaScript**: no se justifica un bundle para cinco números.

## Criterio de aceptación

- [ ] Página en `/admin/costos/vista`, protegida con la misma API key
- [ ] Total, proyección, desglose por categoría y bloque de eficiencia
- [ ] Gráfica de gasto diario
- [ ] Comparación contra el mes anterior
- [ ] Legible en el celular de Gabriel, no solo en escritorio
- [ ] Cero dependencias de JavaScript externas
