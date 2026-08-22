import hashlib
import hmac

PREFIJO_FIRMA = "sha256="


def validar_firma(cuerpo: bytes, firma_recibida: str | None, secreto: str) -> bool:
    """Verifica que un webhook de Meta venga firmado con el App Secret correcto.

    Meta calcula HMAC-SHA256 sobre el body exacto que envía y lo manda en el
    header X-Hub-Signature-256. Esta función recalcula esa firma sobre el
    mismo body y compara. Solo alguien que conozca el secreto puede producir
    una firma que coincida.

    Args:
        cuerpo: Bytes crudos del body, tal como llegaron por la red. Debe ser
            el resultado de `await request.body()`, nunca un JSON reserializado
            (reserializar cambia espacios y orden de llaves, y la firma deja
            de coincidir aunque el mensaje sea legítimo).
        firma_recibida: Valor del header X-Hub-Signature-256, con el prefijo
            "sha256=". None si el header no vino en la petición.
        secreto: El WHATSAPP_APP_SECRET compartido con Meta.

    Returns:
        True si la firma es válida, False en cualquier otro caso (header
        ausente, prefijo faltante, o firma que no coincide).
    """
    if firma_recibida is None or not firma_recibida.startswith(PREFIJO_FIRMA):
        return False

    firma_dada = firma_recibida[len(PREFIJO_FIRMA):]
    firma_esperada = hmac.new(secreto.encode(), cuerpo, hashlib.sha256).hexdigest()

    # compare_digest tarda el mismo tiempo sin importar en qué carácter
    # difieren las dos cadenas; == se detiene en el primer byte distinto y
    # ese tiempo variable es explotable (timing attack).
    return hmac.compare_digest(firma_esperada, firma_dada)
