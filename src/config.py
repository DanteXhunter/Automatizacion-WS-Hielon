from datetime import time
from decimal import Decimal
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    whatsapp_access_token: SecretStr
    whatsapp_phone_number_id: str
    whatsapp_verify_token: str
    whatsapp_app_secret: SecretStr
    whatsapp_telefono_admin: str | None = None
    hora_inicio: time = time(7, 0)
    hora_fin: time = time(17, 0)
    hora_corte_mismo_dia: time = time(14, 0)
    timezone: str = "America/Mexico_City"
    tarifa_service_mxn: Decimal = Decimal("0.1565")
    tarifa_utility_mxn: Decimal = Decimal("0.1565")
    tarifa_authentication_mxn: Decimal = Decimal("0.1565")
    tarifa_marketing_mxn: Decimal = Decimal("0.5614")
    alerta_gasto_mensual_mxn: Decimal = Decimal("2000")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
