"""Consultas y operaciones de pedidos usadas por la conversación."""

from decimal import Decimal
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.pedido import EstadoPedido, Pedido
from src.models.pedido_item import PedidoItem
from src.models.producto import Producto


async def listar_productos_activos(session: AsyncSession) -> list[Producto]:
    """Devuelve el catálogo vendible ordenado por presentación."""
    resultado = await session.exec(
        select(Producto)
        .where(Producto.activo.is_(True))
        .order_by(Producto.peso_kg, Producto.nombre)
    )
    return list(resultado.all())


async def obtener_producto_activo(
    session: AsyncSession, producto_id: UUID
) -> Producto | None:
    """Busca un producto por UUID y rechaza los que ya no están activos."""
    resultado = await session.exec(
        select(Producto).where(
            Producto.id == producto_id,
            Producto.activo.is_(True),
        )
    )
    return resultado.first()


async def obtener_o_crear_borrador(
    session: AsyncSession, cliente_id: UUID, borrador_id: UUID | None
) -> Pedido:
    """Recupera el borrador actual o crea uno si todavía no existe."""
    if borrador_id is not None:
        resultado = await session.exec(
            select(Pedido).where(
                Pedido.id == borrador_id,
                Pedido.cliente_id == cliente_id,
                Pedido.estado == EstadoPedido.BORRADOR,
            )
        )
        pedido = resultado.first()
        if pedido is not None:
            return pedido

    existente = await session.exec(
        select(Pedido)
        .where(
            Pedido.cliente_id == cliente_id,
            Pedido.estado == EstadoPedido.BORRADOR,
        )
        .order_by(Pedido.created_at.desc())
        .limit(1)
    )
    pedido_existente = existente.first()
    if pedido_existente is not None:
        return pedido_existente

    pedido = Pedido(cliente_id=cliente_id, estado=EstadoPedido.BORRADOR)
    session.add(pedido)
    await session.flush()
    return pedido


async def obtener_borrador(
    session: AsyncSession, cliente_id: UUID, borrador_id: UUID | None
) -> Pedido | None:
    """Obtiene el borrador de la conversación sin crear uno implícitamente."""
    consulta = select(Pedido).where(
        Pedido.cliente_id == cliente_id,
        Pedido.estado == EstadoPedido.BORRADOR,
    )
    if borrador_id is not None:
        consulta = consulta.where(Pedido.id == borrador_id)
    return (await session.exec(consulta)).first()


async def agregar_item_borrador(
    session: AsyncSession,
    pedido: Pedido,
    producto: Producto,
    cantidad: int,
) -> PedidoItem:
    """Agrega una línea con snapshot del precio y actualiza el total."""
    subtotal = (producto.precio * cantidad).quantize(Decimal("0.01"))
    item = PedidoItem(
        pedido_id=pedido.id,
        producto_id=producto.id,
        cantidad=cantidad,
        precio_unitario=producto.precio,
        subtotal=subtotal,
    )
    session.add(item)
    await session.flush()
    pedido.total = await calcular_total_borrador(session, pedido.id)
    return item


async def calcular_total_borrador(session: AsyncSession, pedido_id: UUID) -> Decimal:
    """Recalcula desde las líneas persistidas; no confía en el contexto FSM."""
    resultado = await session.exec(
        select(PedidoItem.subtotal).where(PedidoItem.pedido_id == pedido_id)
    )
    return sum(resultado.all(), Decimal("0.00")).quantize(Decimal("0.01"))


async def listar_items_borrador(
    session: AsyncSession, pedido_id: UUID
) -> list[tuple[PedidoItem, Producto]]:
    """Devuelve las líneas del carrito junto a su producto, sin lazy loading."""
    resultado = await session.exec(
        select(PedidoItem, Producto)
        .join(Producto, Producto.id == PedidoItem.producto_id)
        .where(PedidoItem.pedido_id == pedido_id)
        .order_by(PedidoItem.id)
    )
    return list(resultado.all())


async def eliminar_item_borrador(
    session: AsyncSession, pedido: Pedido, item_id: UUID
) -> bool:
    """Elimina una línea indicada y vuelve a calcular el total persistido."""
    resultado = await session.exec(
        select(PedidoItem).where(
            PedidoItem.id == item_id,
            PedidoItem.pedido_id == pedido.id,
        )
    )
    item = resultado.first()
    if item is None:
        return False

    await session.delete(item)
    await session.flush()
    pedido.total = await calcular_total_borrador(session, pedido.id)
    return True


async def vaciar_items_borrador(session: AsyncSession, pedido: Pedido) -> None:
    """Elimina todas las líneas del borrador y deja su total consistente en cero."""
    resultado = await session.exec(
        select(PedidoItem).where(PedidoItem.pedido_id == pedido.id)
    )
    for item in resultado.all():
        await session.delete(item)
    await session.flush()
    pedido.total = await calcular_total_borrador(session, pedido.id)


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
