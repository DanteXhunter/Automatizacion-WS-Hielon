## Depende de

- #79 — línea base medida
- #42 — pedidos confirmados en base con sus items

## Objetivo

Que un cliente recurrente pueda cerrar un pedido en **2 mensajes** en vez de 7.

**Delta de MSPC esperado: -5 en el camino feliz. Es el ahorro más grande de la
Fase 3.5.**

## Por qué este es el issue que más importa

La clientela de Hielon son **mayoristas recurrentes**: restaurantes y tienditas
que piden casi lo mismo cada vez. Optimizar el flujo de captura completo para
alguien que va a pedir "lo de siempre" es resolver el problema equivocado.

Los otros issues de la fase raspan 1-2 mensajes. Este quita 5.

## Flujo propuesto

```
Cliente: "hola"

Bot (1): "Buenos dias {nombre}. ¿Repetimos lo de siempre?
          10 bolsas de 5 kg - $XXX
          A: Av. Lopez Mateos 1234
          [Si, confirmar] [Cambiar pedido] [Otra direccion]"

Cliente: [Si, confirmar]

Bot (2): "Listo. Pedido #2026-0142 confirmado."
```

Dos mensajes salientes: MX$0.31 por pedido contra MX$1.10.

## Cuándo se ofrece el atajo

Solo si se cumple **todo**:

- El cliente tiene al menos un pedido en estado `entregado`
- Su último pedido tiene 3 o menos líneas (si no, no cabe en el body)
- Tiene una dirección marcada `es_ultima_usada`
- Todos los productos de ese pedido siguen `activo = true`

Si algo falla, se cae al flujo normal sin avisar nada. **No gastar un mensaje
en explicar por qué no hay atajo.**

## Qué pedido se repite

El **último entregado**, no el más frecuente. Es más predecible para el cliente
y no requiere análisis de histórico. Si más adelante hay datos suficientes, se
puede revisar.

## Precio

Se recalcula con el precio **actual** del catálogo, no el del pedido anterior.
Si cambió, el resumen lo muestra ya actualizado; el cliente ve el precio que va
a pagar antes de confirmar.

## Criterio de aceptación

- [ ] `IDLE` detecta cliente elegible y ofrece el atajo en el primer mensaje
- [ ] Camino feliz confirmado: 2 mensajes salientes, verificado en `mensajes`
- [ ] `Cambiar pedido` cae al flujo normal desde `SELECCIONANDO_PRODUCTO`
- [ ] `Otra direccion` salta directo a `CAPTURANDO_DIRECCION` conservando items
- [ ] Precio recalculado con el catálogo vigente
- [ ] Cliente no elegible ve el flujo normal, sin mensaje extra
