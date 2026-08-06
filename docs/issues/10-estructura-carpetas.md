## Objetivo

Crear **únicamente** los archivos que la Fase 1 necesita, no el árbol completo.

## Decisión (6-ago-2026): estructura incremental

El árbol documentado en `CLAUDE.md` es un **mapa de destino**, no una lista de
creación. En disco solo existe lo que ya se usa.

**Regla: un archivo nace cuando su ausencia duele.** Se escribe el código donde
quepa, y cuando el archivo se pone incómodo, se extrae lo que corresponde.

Por qué, dado que el objetivo del proyecto es aprender: 13 carpetas vacías con
`__init__.py` no enseñan nada y producen la sensación de rellenar huecos de una
plantilla ajena. El costo de mover código a su lugar definitivo después es
trivial; el costo de la estructura prematura es no entender por qué existe cada
separación.

## Qué se crea en este issue

```
.env.example
.gitignore
requirements.txt
src/
├── __init__.py
├── main.py              # se llena en el issue #12
└── config.py            # se llena en el issue #13
tests/
└── __init__.py
```

Nada más. `src/api/`, `src/whatsapp/` y `tests/unit/` nacen cuando su primer
archivo lo necesite (issues #15 y #18).

## Qué NO se crea, y en qué issue nace cada cosa

| Carpeta | Nace en | Disparador |
|---|---|---|
| `src/api/` | #15 | primer endpoint del webhook |
| `src/whatsapp/` | #18 | validación HMAC |
| `tests/unit/` | #20 | primer test |
| `src/models/`, `database.py` | #22 | primeras tablas SQLModel |
| `src/fsm/` | #27 | enum de estados |
| `src/services/` | #25 | `cliente_service` |
| `src/utils/` | #32 | helpers de horario |
| `src/notifications/` | #48 | handoff a Gabriel |
| `src/schemas/` | cuando haga falta | puede que nunca en v1 |

## Por qué `src/` y no la raíz

Es el estándar de la industria en Python. La razón técnica de fondo
(resolución de imports y el fallo "en mi máquina sí jala") se explica en la
Fase 5, cuando se despliegue y el problema sea tangible. Aquí se adopta la
convención sin necesidad de justificarla a fondo todavía.

## Criterio de aceptación

- [ ] Existen exactamente los archivos listados arriba, ni uno más
- [ ] `python -c "import src"` no truena
- [ ] `.gitignore` incluye `.env`, `__pycache__/`, `.venv/`
- [ ] No hay carpetas vacías con `__init__.py` "por si acaso"

Nota: el contenido de `main.py` y `config.py` se escribe en los issues #12 y
#13. Aquí solo se crean los archivos.
