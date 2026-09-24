"""Consultas y escrituras transaccionales de direcciones de clientes."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.direccion import Direccion


async def obtener_ultima_direccion(
    session: AsyncSession, cliente_id: UUID
) -> Direccion | None:
    """Busca la marcada como última; si ninguna lo está, usa la más reciente."""
    resultado = await session.exec(
        select(Direccion)
        .where(Direccion.cliente_id == cliente_id, Direccion.es_ultima_usada.is_(True))
        .order_by(Direccion.created_at.desc())
        .limit(1)
    )
    direccion = resultado.first()
    if direccion is not None:
        return direccion

    resultado = await session.exec(
        select(Direccion)
        .where(Direccion.cliente_id == cliente_id)
        .order_by(Direccion.created_at.desc())
        .limit(1)
    )
    return resultado.first()


async def marcar_ultima_direccion(
    session: AsyncSession, cliente_id: UUID, direccion: Direccion
) -> None:
    """Garantiza una sola dirección preferida para el cliente en la transacción."""
    await session.exec(
        update(Direccion)
        .where(Direccion.cliente_id == cliente_id)
        .values(es_ultima_usada=False)
    )
    direccion.es_ultima_usada = True


async def guardar_direccion(
    session: AsyncSession,
    cliente_id: UUID,
    *,
    texto: str | None,
    latitud: Decimal | None = None,
    longitud: Decimal | None = None,
) -> Direccion:
    """Desmarca la dirección anterior y guarda la nueva como última usada."""
    await session.exec(
        update(Direccion)
        .where(Direccion.cliente_id == cliente_id, Direccion.es_ultima_usada.is_(True))
        .values(es_ultima_usada=False)
    )
    direccion = Direccion(
        cliente_id=cliente_id,
        texto=texto,
        latitud=latitud,
        longitud=longitud,
        es_ultima_usada=True,
    )
    session.add(direccion)
    await session.flush()
    return direccion
