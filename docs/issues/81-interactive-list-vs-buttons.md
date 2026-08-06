## Depende de

- #79 — línea base medida

## Objetivo

Decidir con datos si conviene reemplazar cadenas de Reply Buttons por una sola
List Message.

**Delta de MSPC esperado: -1 a -2.**

## El caso concreto

Hoy elegir producto y cantidad cuesta 2 mensajes:

```
1. "¿Qué producto?"        [3kg] [5kg] [10kg]
2. "¿Cuántas bolsas?"      (texto libre)
```

Una List Message admite hasta **10 filas repartidas en secciones** en un solo
envío. Para mayoristas recurrentes, las combinaciones frecuentes caben:

```
Bolsa 5 kg - 10 piezas
Bolsa 5 kg - 20 piezas
Bolsa 10 kg - 10 piezas
Bolsa 3 kg - 20 piezas
Otra cantidad...
```

Un solo mensaje, una sola selección.

## Trade-off honesto

**A favor**: menos mensajes, menos errores de captura (no hay texto libre que
validar), más rápido para el cliente recurrente.

**En contra**: la lista se abre en un menú aparte, no se ve en el hilo del
chat. Para el cliente nuevo es más fricción que tres botones visibles. Y el
catálogo de combinaciones hay que mantenerlo.

## Cómo decidir

No por intuición. Implementar las dos variantes y comparar sobre pedidos
reales: MSPC, tasa de abandono a mitad de flujo y tasa de entradas inválidas.

Si la lista baja el MSPC pero sube el abandono, **no conviene**: un pedido
perdido cuesta más que 10 mensajes.

## Criterio de aceptación

- [ ] Helper de List Message implementado en `src/whatsapp/messages.py`
- [ ] Las combinaciones se derivan del historial real, no se inventan
- [ ] Opción de escape "Otra cantidad" que cae al flujo actual
- [ ] Comparadas ambas variantes con MSPC y tasa de abandono
- [ ] Decisión documentada con los números que la respaldan
