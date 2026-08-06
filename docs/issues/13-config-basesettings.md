## Depende de

- #11 — `.env.example` define el contrato de variables
- #12 — app FastAPI existente

Se puede cerrar con valores dummy en el `.env`; no requiere credenciales
reales de Meta.

## Objetivo

Centralizar toda la configuración en un objeto tipado y validado, cargado una
sola vez al arrancar.

## Contexto

`pydantic-settings` lee variables de entorno y las valida contra un modelo. La
ventaja sobre `os.getenv()` regado por el código: si falta una variable o
tiene el tipo equivocado, **la app no arranca** y te dice exactamente cuál.
Es mucho mejor que reventar a las 3 AM en el cron de recordatorios.

## Alcance

`src/config.py` con una clase `Settings(BaseSettings)` que declare:

| Campo | Tipo | Obligatorio |
|---|---|---|
| `database_url` | str | sí |
| `whatsapp_access_token` | SecretStr | sí |
| `whatsapp_phone_number_id` | str | sí |
| `whatsapp_verify_token` | str | sí |
| `whatsapp_app_secret` | SecretStr | sí |
| `telegram_bot_token` | SecretStr | no |
| `telegram_chat_id` | str | no |
| `hora_inicio` | time | no, default 07:00 |
| `hora_fin` | time | no, default 17:00 |
| `hora_corte_mismo_dia` | time | no, default 14:00 |
| `timezone` | str | no, default America/Mexico_City |

Exponer una instancia única cacheada con `@lru_cache`.

## SecretStr

Tipo de Pydantic que enmascara el valor al imprimirse: `repr()` muestra
`SecretStr('**********')` en vez del token. Evita que un `print(settings)` o
un traceback en los logs filtre el token de Meta. Para leer el valor real se
usa `.get_secret_value()`.

## Criterio de aceptación

- [ ] La app falla al arrancar si falta una variable obligatoria, con mensaje
      claro de cuál
- [ ] Los tokens usan `SecretStr`
- [ ] Ningún módulo lee `os.environ` directamente; todos importan `settings`
- [ ] Imprimir el objeto settings no revela ningún secreto
