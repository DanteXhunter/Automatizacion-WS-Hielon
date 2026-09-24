"""Consultas y reglas transaccionales del ciclo de vida de los pedidos."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.direccion import Direccion
from src.models.pedido import EstadoPedido, Pedido
from src.models.pedido_item import PedidoItem
from src.models.producto import Producto
from src.utils.datetime import ahora_local


class TransicionPedidoInvalidaError(ValueError):
    """Impide mover un pedido a un estado incompatible con su ciclo de vida."""


class PedidoNoEncontradoError(LookupError):
    """Indica que el borrador solicitado no pertenece al cliente."""


class PedidoSinItemsError(ValueError):
    """Indica que un borrador vacío no puede confirmarse."""


class PedidoSinDireccionError(ValueError):
    """Indica que falta una dirección válida antes de confirmar."""


TRANSICIONES_PEDIDO: dict[EstadoPedido, frozenset[EstadoPedido]] = {
    EstadoPedido.BORRADOR: frozenset(
        {EstadoPedido.PENDIENTE, EstadoPedido.CANCELADO_CLIENTE}
    ),
    EstadoPedido.PENDIENTE: frozenset(
        {
            EstadoPedido.PROGRAMADO,
            EstadoPedido.EN_RUTA,
            EstadoPedido.CANCELADO_NEGOCIO,
            EstadoPedido.CANCELADO_CLIENTE,
        }
    ),
    EstadoPedido.PROGRAMADO: frozenset(
        {
            EstadoPedido.EN_RUTA,
            EstadoPedido.CANCELADO_NEGOCIO,
            EstadoPedido.CANCELADO_CLIENTE,
        }
    ),
    EstadoPedido.EN_RUTA: frozenset(
        {EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO_NEGOCIO}
    ),
    EstadoPedido.ENTREGADO: frozenset(),
    EstadoPedido.CANCELADO_CLIENTE: frozenset(),
    EstadoPedido.CANCELADO_NEGOCIO: frozenset(),
}


@dataclass(frozen=True)
class ResultadoConfirmacionPedido:
    """Datos que el handler necesita después de preparar el commit."""

    pedido: Pedido
    es_primer_pedido: bool
    ya_estaba_confirmado: bool = False


def cambiar_estado(pedido: Pedido, nuevo_estado: EstadoPedido) -> None:
    """Aplica una transición válida; repetir el estado actual es un no-op."""
    if pedido.estado == nuevo_estado:
        return
    permitidos = TRANSICIONES_PEDIDO[pedido.estado]
    if nuevo_estado not in permitidos:
        raise TransicionPedidoInvalidaError(
            f"No se puede cambiar un pedido de {pedido.estado.value} "
            f"a {nuevo_estado.value}."
        )
    pedido.estado = nuevo_estado


async def generar_numero_orden(
    session: AsyncSession,
    *,
    anio: int | None = None,
) -> str:
    """Reserva atómicamente el siguiente consecutivo del año en PostgreSQL."""
    anio_folio = anio if anio is not None else ahora_local().year
    resultado = await session.exec(
        text("""
            INSERT INTO folios_pedido_anuales (anio, ultimo_valor)
            VALUES (:anio, 1)
            ON CONFLICT (anio)
            DO UPDATE SET ultimo_valor = folios_pedido_anuales.ultimo_valor + 1
            RETURNING ultimo_valor
            """),
        params={"anio": anio_folio},
    )
    consecutivo = int(resultado.scalar_one())
    return f"{anio_folio}-{consecutivo:04d}"


async def confirmar_pedido(
    session: AsyncSession,
    cliente_id: UUID,
    pedido_id: UUID | None,
) -> ResultadoConfirmacionPedido:
    """Valida y convierte un borrador en pendiente dentro de la sesión actual."""
    if pedido_id is None:
        raise PedidoNoEncontradoError("La conversación no tiene un borrador asociado.")

    resultado = await session.exec(
        select(Pedido)
        .where(Pedido.id == pedido_id, Pedido.cliente_id == cliente_id)
        .with_for_update()
    )
    pedido = resultado.first()
    if pedido is None:
        raise PedidoNoEncontradoError("No se encontró el pedido del cliente.")
    if pedido.estado == EstadoPedido.PENDIENTE and pedido.numero_orden:
        return ResultadoConfirmacionPedido(
            pedido=pedido,
            es_primer_pedido=False,
            ya_estaba_confirmado=True,
        )
    if pedido.estado != EstadoPedido.BORRADOR:
        raise TransicionPedidoInvalidaError(
            f"El pedido está en estado {pedido.estado.value} y no puede confirmarse."
        )

    items = await listar_items_borrador(session, pedido.id)
    if not items:
        raise PedidoSinItemsError("El pedido no contiene productos.")
    if pedido.direccion_id is None:
        raise PedidoSinDireccionError("El pedido no tiene dirección de entrega.")
    direccion = (
        await session.exec(
            select(Direccion).where(
                Direccion.id == pedido.direccion_id,
                Direccion.cliente_id == cliente_id,
            )
        )
    ).first()
    if direccion is None:
        raise PedidoSinDireccionError("La dirección no pertenece al cliente.")

    pedido_previo = (
        await session.exec(
            select(Pedido.id)
            .where(
                Pedido.cliente_id == cliente_id,
                Pedido.id != pedido.id,
                Pedido.estado != EstadoPedido.BORRADOR,
            )
            .limit(1)
        )
    ).first()
    pedido.total = await calcular_total_borrador(session, pedido.id)
    pedido.numero_orden = await generar_numero_orden(session)
    cambiar_estado(pedido, EstadoPedido.PENDIENTE)
    await session.flush()
    return ResultadoConfirmacionPedido(
        pedido=pedido,
        es_primer_pedido=pedido_previo is None,
    )


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
