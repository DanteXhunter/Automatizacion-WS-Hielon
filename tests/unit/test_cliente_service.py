import pytest

from src.services.cliente_service import normalizar_telefono


@pytest.mark.parametrize(
    ("telefono_entrada", "telefono_esperado"),
    [
        ("5214771234567", "+5214771234567"),
        ("+5214771234567", "+5214771234567"),
        ("+52 477 123 4567", "+5214771234567"),
    ],
)
def test_normalizar_telefono_conserva_un_solo_formato_e164(
    telefono_entrada: str,
    telefono_esperado: str,
):
    assert normalizar_telefono(telefono_entrada) == telefono_esperado


@pytest.mark.parametrize("telefono", ["", "+5214771234abc", "+0014771234567"])
def test_normalizar_telefono_rechaza_formatos_invalidos(telefono: str):
    with pytest.raises(ValueError, match="E.164"):
        normalizar_telefono(telefono)
