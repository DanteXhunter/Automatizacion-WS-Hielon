"""Concurrencia real del contador anual de folios en PostgreSQL."""

import asyncio
import os

import pytest
from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.services.pedido_service import generar_numero_orden

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Define TEST_DATABASE_URL con una base PostgreSQL migrada para pruebas.",
)


@pytest.mark.asyncio
async def test_cincuenta_folios_concurrentes_son_distintos() -> None:
    assert TEST_DATABASE_URL is not None
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=pool.NullPool)
    fabrica = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    anio_prueba = 2099

    async with fabrica() as session:
        await session.exec(
            text("DELETE FROM folios_pedido_anuales WHERE anio = :anio"),
            params={"anio": anio_prueba},
        )
        await session.commit()

    async def reservar() -> str:
        async with fabrica() as session:
            folio = await generar_numero_orden(session, anio=anio_prueba)
            await session.commit()
            return folio

    try:
        folios = await asyncio.gather(*(reservar() for _ in range(50)))
        assert len(set(folios)) == 50
        assert min(folios) == "2099-0001"
        assert max(folios) == "2099-0050"
    finally:
        async with fabrica() as session:
            await session.exec(
                text("DELETE FROM folios_pedido_anuales WHERE anio = :anio"),
                params={"anio": anio_prueba},
            )
            await session.commit()
        await engine.dispose()
