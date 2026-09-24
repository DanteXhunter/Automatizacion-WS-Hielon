"""Límites del horario de Hielon, independientemente de la zona del servidor."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from src.utils.datetime import (
    ahora_local,
    es_dia_habil,
    es_horario_laboral,
    paso_hora_corte,
)

LEON = ZoneInfo("America/Mexico_City")


@pytest.mark.parametrize(
    ("hora", "minuto", "esperado"),
    [
        (6, 59, False),
        (7, 0, True),
        (13, 59, True),
        (14, 0, True),
        (16, 59, True),
        (17, 0, False),
    ],
)
def test_bordes_del_horario(hora: int, minuto: int, esperado: bool) -> None:
    lunes = datetime(2026, 9, 21, hora, minuto, tzinfo=LEON)
    assert es_horario_laboral(lunes) is esperado
    assert es_horario_laboral(lunes.astimezone(timezone.utc)) is esperado


def test_domingo_cerrado_y_sabado_habil() -> None:
    sabado = datetime(2026, 9, 26, 10, tzinfo=LEON)
    domingo = datetime(2026, 9, 27, 10, tzinfo=LEON)
    assert es_dia_habil(sabado)
    assert es_horario_laboral(sabado)
    assert not es_dia_habil(domingo)
    assert not es_horario_laboral(domingo)


@pytest.mark.parametrize(
    ("hora", "minuto", "esperado"),
    [(13, 59, False), (14, 0, False), (14, 1, True)],
)
def test_corte_del_mismo_dia(hora: int, minuto: int, esperado: bool) -> None:
    instante = datetime(2026, 9, 21, hora, minuto, tzinfo=LEON)
    assert paso_hora_corte(instante) is esperado


def test_ahora_local_incluye_zona_y_fecha_sin_zona_se_rechaza() -> None:
    assert ahora_local().tzinfo == LEON
    fecha_ingenua = datetime(2026, 9, 21, 10)  # noqa: DTZ001 - prueba fecha ingenua
    with pytest.raises(ValueError, match="zona horaria"):
        es_horario_laboral(fecha_ingenua)
