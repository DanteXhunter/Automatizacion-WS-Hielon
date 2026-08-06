## Idea de backlog

Agregar una capa opcional de LLM para interpretar mensajes en lenguaje
natural (por ejemplo, entender "mándame 10 de 5 kilos" sin pasar por los
botones) y normalizar direcciones de texto libre.

## Alcance futuro

- El LLM interpretaría la intención y la traduciría a los mismos eventos que
  hoy generan los botones, **sin reemplazar la FSM determinista**: la FSM
  seguiría siendo la que decide transiciones válidas y mantiene el estado
  consistente, evitando alucinaciones que confirmen o cancelen algo por error
- Fallback: si el LLM no logra interpretar con confianza suficiente, se cae al
  flujo de botones actual
- Costo adicional por llamada a modelo, a evaluar contra el beneficio real en
  fricción de usuario

## Por qué no en v1

`claude.md` cierra la decisión explícitamente: "Sin LLM en v1. Todo el flujo
se resuelve con máquina de estados determinista." La razón de fondo es
confiabilidad y costo: un flujo de pedidos con dinero real de por medio se
beneficia más de ser 100% predecible que de aceptar lenguaje libre.
