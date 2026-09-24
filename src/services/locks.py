"""Serialización transaccional de conversaciones por cliente en PostgreSQL."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession


@asynccontextmanager
async def bloqueo_por_cliente(
    session: AsyncSession, cliente_id: UUID
) -> AsyncIterator[None]:
    """Toma un lock hasta el commit o rollback de la transacción actual.

    La clave proviene del UUID completo. Una colisión de ``hashtext`` solo
    serializaría de más a dos clientes distintos; no mezclaría sus datos.
    """
    await session.exec(
        text("SELECT pg_advisory_xact_lock(hashtext(:cliente_id)::bigint)"),
        params={"cliente_id": str(cliente_id)},
    )
    try:
        yield
    except BaseException:
        # Si el handler falla antes del commit, el rollback libera el lock.
        await session.rollback()
        raise
