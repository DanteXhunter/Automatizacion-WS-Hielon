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
| `whatsapp_telefono_admin` | str | no |
| `hora_inicio` | time | no, default 07:00 |
| `hora_fin` | time | no, default 17:00 |
| `hora_corte_mismo_dia` | time | no, default 14:00 |
| `timezone` | str | no, default America/Mexico_City |
| `tarifa_service_mxn` | Decimal | no, default 0.1565 |
| `tarifa_utility_mxn` | Decimal | no, default 0.1565 |
| `tarifa_authentication_mxn` | Decimal | no, default 0.1565 |
| `tarifa_marketing_mxn` | Decimal | no, default 0.8000 |
| `alerta_gasto_mensual_mxn` | Decimal | no, default 2000 |

## Por qué las tarifas son configuración y no constantes

Meta cambió el modelo de cobro el 1-oct-2026 y volverá a cambiarlo. Si las
tarifas están hardcodeadas, actualizarlas obliga a un deploy y **reescribe
retroactivamente el costo de los mensajes ya enviados** en cualquier cálculo
que las lea. Como variable de entorno, se ajusta el valor sin tocar código y
el `costo_estimado` ya guardado en `mensajes` (snapshot) conserva la tarifa
que de verdad se pagó.

`Decimal` y no `float`: son cantidades de dinero. `float` acumula error de
redondeo binario y al sumar miles de mensajes el total deja de cuadrar con la
factura de Meta.

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
