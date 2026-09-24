"""Reglas de calendario y horario expresadas en la zona local del negocio."""

from datetime import datetime
from zoneinfo import ZoneInfo

from src.config import settings


def ahora_local() -> datetime:
    """Devuelve la hora actual con la zona configurada para Hielon."""
    return datetime.now(ZoneInfo(settings.timezone))


def _en_zona_local(dt: datetime | None) -> datetime:
    """Convierte una fecha consciente a la zona local; nunca adivina una zona."""
    if dt is None:
        return ahora_local()
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("La fecha debe incluir zona horaria.")
    return dt.astimezone(ZoneInfo(settings.timezone))


def es_dia_habil(dt: datetime | None = None) -> bool:
    """Indica si en León es lunes a sábado."""
    return _en_zona_local(dt).weekday() < 6


def es_horario_laboral(dt: datetime | None = None) -> bool:
    """Aplica el inicio inclusivo y el cierre exclusivo del horario laboral."""
    local = _en_zona_local(dt)
    return (
        local.weekday() < 6 and settings.hora_inicio <= local.time() < settings.hora_fin
    )


def paso_hora_corte(dt: datetime | None = None) -> bool:
    """Indica si ya pasó la hora límite de pedidos para el mismo día."""
    return _en_zona_local(dt).time() > settings.hora_corte_mismo_dia
