"""Siembra el catálogo inicial de Hielon sin duplicar productos existentes."""

import asyncio
from decimal import Decimal

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.producto import Producto

# Gabriel aún no confirma precios ni dos dimensiones. Cero deja evidente que son
# valores provisionales y evita inventar un precio que pudiera llegar a usarse.
PRODUCTOS_INICIALES: tuple[dict[str, object], ...] = (
    {
        "nombre": "Bolsa 3 kg",
        "peso_kg": Decimal(3),
        "dimensiones": "Pendiente de confirmar",
        "precio": Decimal("0.00"),
        "activo": True,
    },
    {
        "nombre": "Bolsa 5 kg",
        "peso_kg": Decimal(5),
        "dimensiones": "30 x 60 cm",
        "precio": Decimal("0.00"),
        "activo": True,
    },
    {
        "nombre": "Bolsa 10 kg",
        "peso_kg": Decimal(10),
        "dimensiones": "Pendiente de confirmar",
        "precio": Decimal("0.00"),
        "activo": True,
    },
)


async def sembrar_productos(session: AsyncSession) -> int:
    """Inserta solo los productos cuyo nombre no exista todavía."""
    creados = 0

    for datos_producto in PRODUCTOS_INICIALES:
        consulta = select(Producto.id).where(
            Producto.nombre == datos_producto["nombre"]
        )
        resultado = await session.exec(consulta)

        if resultado.first() is None:
            session.add(Producto(**datos_producto))
            creados += 1

    await session.commit()
    return creados


async def main() -> None:
    """Abre una sesión de la app, siembra el catálogo y la cierra."""
    from src.database import session_factory

    async with session_factory() as session:
        creados = await sembrar_productos(session)

    print(f"Productos creados: {creados}")


if __name__ == "__main__":
    asyncio.run(main())
