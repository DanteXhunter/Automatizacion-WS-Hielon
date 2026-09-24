"""Consultas puntuales de pedidos usadas por la conversación."""

from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.pedido import EstadoPedido, Pedido


async def obtener_ultimo_pedido_activo(
    session: AsyncSession, cliente_id: UUID
) -> Pedido | None:
    """Busca el pedido activo más reciente de un cliente."""
    resultado = await session.exec(
        select(Pedido)
        .where(
            Pedido.cliente_id == cliente_id,
            Pedido.estado.in_(
                [EstadoPedido.PENDIENTE, EstadoPedido.PROGRAMADO, EstadoPedido.EN_RUTA]
            ),
        )
        .order_by(Pedido.created_at.desc())
        .limit(1)
    )
    return resultado.first()
