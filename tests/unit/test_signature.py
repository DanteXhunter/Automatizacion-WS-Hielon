import hashlib
import hmac

from src.whatsapp.signature import validar_firma

SECRETO_PRUEBA = "un-secreto-de-prueba-nunca-el-real"


def firmar(cuerpo: bytes, secreto: str = SECRETO_PRUEBA) -> str:
    """Genera una firma X-Hub-Signature-256 válida, igual que la haría Meta."""
    return "sha256=" + hmac.new(secreto.encode(), cuerpo, hashlib.sha256).hexdigest()


def test_firma_valida_sobre_body_correcto_pasa():
    cuerpo = b'{"entry": []}'
    assert validar_firma(cuerpo, firmar(cuerpo), SECRETO_PRUEBA) is True


def test_firma_calculada_con_otro_secreto_rechaza():
    cuerpo = b'{"entry": []}'
    firma_con_secreto_equivocado = firmar(cuerpo, secreto="otro-secreto")
    assert validar_firma(cuerpo, firma_con_secreto_equivocado, SECRETO_PRUEBA) is False


def test_header_ausente_rechaza():
    cuerpo = b'{"entry": []}'
    assert validar_firma(cuerpo, None, SECRETO_PRUEBA) is False


def test_header_sin_prefijo_sha256_rechaza():
    cuerpo = b'{"entry": []}'
    firma_sin_prefijo = firmar(cuerpo).removeprefix("sha256=")
    assert validar_firma(cuerpo, firma_sin_prefijo, SECRETO_PRUEBA) is False


def test_body_alterado_un_byte_con_firma_original_rechaza():
    cuerpo_original = b'{"entry": []}'
    firma_del_original = firmar(cuerpo_original)
    cuerpo_alterado = b'{"entry": [}'  # un carácter distinto
    assert validar_firma(cuerpo_alterado, firma_del_original, SECRETO_PRUEBA) is False


def test_body_vacio_rechaza_sin_excepcion():
    # El caso límite: cuerpo de longitud cero no debe tronar la función,
    # solo rechazar si la firma no corresponde.
    assert validar_firma(b"", "sha256=firma-que-no-corresponde", SECRETO_PRUEBA) is False


def test_firma_en_mayusculas_rechaza():
    # Decisión documentada: hexdigest() siempre produce minúsculas y
    # compare_digest exige coincidencia exacta byte a byte, así que una
    # firma válida pero en mayúsculas se rechaza. No es un caso real de
    # Meta (Meta siempre manda minúsculas), pero queda cubierto y decidido.
    cuerpo = b'{"entry": []}'
    firma_en_mayusculas = firmar(cuerpo).upper()
    assert validar_firma(cuerpo, firma_en_mayusculas, SECRETO_PRUEBA) is False
