"""Operaciones para identificar clientes a partir de su teléfono."""

import re
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.cliente import Cliente

_SEPARADORES_TELEFONO = re.compile(r"[\s()\-]")
_E164 = re.compile(r"^\+[1-9]\d{7,14}$")


def normalizar_telefono(telefono: str) -> str:
    """Convierte formatos de Meta o panel al formato E.164 almacenado.

    Se conserva el ``1`` que Meta entrega después de ``52`` en números móviles
    mexicanos. Si el panel recibe el formato local ``+52`` seguido por diez
    dígitos, se agrega ese ``1`` para que los tres formatos usen la misma clave.
    """
    telefono_sin_separadores = _SEPARADORES_TELEFONO.sub("", telefono)
    telefono_e164 = (
        telefono_sin_separadores
        if telefono_sin_separadores.startswith("+")
        else f"+{telefono_sin_separadores}"
    )

    if re.fullmatch(r"\+52\d{10}", telefono_e164):
        telefono_e164 = f"+521{telefono_e164[3:]}"

    if not _E164.fullmatch(telefono_e164):
        raise ValueError("El teléfono debe ser un número válido en formato E.164.")

    return telefono_e164


async def get_or_create_por_telefono(
    session: AsyncSession,
    telefono: str,
    nombre: str | None = None,
) -> Cliente:
    """Crea o devuelve un cliente sin riesgo de duplicarlo por concurrencia."""
    telefono_normalizado = normalizar_telefono(telefono)
    ahora = datetime.now(timezone.utc)
    insercion = insert(Cliente).values(
        telefono=telefono_normalizado,
        nombre=nombre,
        created_at=ahora,
        updated_at=ahora,
    )
    sentencia = insercion.on_conflict_do_update(
        index_elements=[Cliente.telefono],
        # No se sobrescribe el nombre: puede haberlo corregido un asesor humano.
        set_={"telefono": insercion.excluded.telefono},
    ).returning(Cliente)

    resultado = await session.exec(sentencia)
    cliente = resultado.scalar_one()
    await session.commit()

    return cliente
