"""Los advisory locks se comprueban con conexiones PostgreSQL independientes."""

import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy import delete, pool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.fsm.dispatcher import DispatcherConversacion, MensajeEntrante, ResultadoHandler
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente
from src.models.conversacion import Conversacion
from src.services.cliente_service import get_or_create_por_telefono
from src.services.locks import bloqueo_por_cliente

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Define TEST_DATABASE_URL con una base PostgreSQL exclusiva para pruebas.",
)


@pytest.mark.asyncio
async def test_mismo_cliente_espera_hasta_commit() -> None:
    assert TEST_DATABASE_URL is not None
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=pool.NullPool)
    fabrica = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    cliente_id = uuid4()
    primero_dentro = asyncio.Event()
    segundo_intenta = asyncio.Event()
    segundo_dentro = asyncio.Event()
    liberar_primero = asyncio.Event()

    async def primero() -> None:
        async with fabrica() as session, bloqueo_por_cliente(session, cliente_id):
            primero_dentro.set()
            await liberar_primero.wait()
            await session.commit()

    async def segundo() -> None:
        await primero_dentro.wait()
        async with fabrica() as session:
            segundo_intenta.set()
            async with bloqueo_por_cliente(session, cliente_id):
                segundo_dentro.set()
                await session.commit()

    tarea_primero = asyncio.create_task(primero())
    tarea_segundo = asyncio.create_task(segundo())
    try:
        await asyncio.wait_for(segundo_intenta.wait(), timeout=2)
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(segundo_dentro.wait(), timeout=0.1)
    finally:
        liberar_primero.set()
        await asyncio.gather(tarea_primero, tarea_segundo)
        await engine.dispose()

    assert segundo_dentro.is_set()


@pytest.mark.asyncio
async def test_clientes_distintos_no_se_bloquean() -> None:
    assert TEST_DATABASE_URL is not None
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=pool.NullPool)
    fabrica = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    primero_dentro = asyncio.Event()
    segundo_dentro = asyncio.Event()
    liberar_primero = asyncio.Event()

    async def primero() -> None:
        async with fabrica() as session, bloqueo_por_cliente(session, uuid4()):
            primero_dentro.set()
            await liberar_primero.wait()
            await session.commit()

    async def segundo() -> None:
        await primero_dentro.wait()
        async with fabrica() as session, bloqueo_por_cliente(session, uuid4()):
            segundo_dentro.set()
            await session.commit()

    tarea_primero = asyncio.create_task(primero())
    tarea_segundo = asyncio.create_task(segundo())
    try:
        await asyncio.wait_for(segundo_dentro.wait(), timeout=2)
    finally:
        liberar_primero.set()
        await asyncio.gather(tarea_primero, tarea_segundo)
        await engine.dispose()


@pytest.mark.asyncio
async def test_dos_mensajes_del_mismo_cliente_no_pierden_items_temporales() -> None:
    assert TEST_DATABASE_URL is not None
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=pool.NullPool)
    fabrica = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    telefono = f"521477{uuid4().int % 10_000_000:07d}"

    async with fabrica() as session:
        cliente = await get_or_create_por_telefono(session, telefono)

    def comenzar(mensaje, _contexto, _cliente, _primera):
        return ResultadoHandler(
            EstadoConversacion.MENU_PRINCIPAL, {"items": [mensaje.valor]}, []
        )

    def continuar(mensaje, contexto, _cliente, _primera):
        return ResultadoHandler(
            EstadoConversacion.MENU_PRINCIPAL,
            {"items": contexto["items"] + [mensaje.valor]},
            [],
        )

    dispatcher = DispatcherConversacion(
        {
            EstadoConversacion.IDLE: comenzar,
            EstadoConversacion.MENU_PRINCIPAL: continuar,
        }
    )

    async def procesar(valor: str) -> None:
        mensaje = MensajeEntrante(tipo="texto", valor=valor, payload={})
        async with fabrica() as session:
            await dispatcher.procesar(session, cliente, mensaje)

    try:
        await asyncio.gather(procesar("bolsa_3kg"), procesar("bolsa_5kg"))
        async with fabrica() as session:
            conversacion = (
                await session.exec(
                    select(Conversacion).where(Conversacion.cliente_id == cliente.id)
                )
            ).one()
            assert sorted(conversacion.contexto["items"]) == ["bolsa_3kg", "bolsa_5kg"]
            assert conversacion.estado_actual == EstadoConversacion.MENU_PRINCIPAL.value
    finally:
        async with fabrica() as session:
            await session.exec(
                delete(Conversacion).where(Conversacion.cliente_id == cliente.id)
            )
            await session.exec(delete(Cliente).where(Cliente.id == cliente.id))
            await session.commit()
        await engine.dispose()
