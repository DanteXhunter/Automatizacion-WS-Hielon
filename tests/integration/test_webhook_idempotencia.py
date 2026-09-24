"""Prueba de webhook duplicado contra una base PostgreSQL exclusiva de tests."""

import asyncio
import hashlib
import hmac
import json
import os
import sys
import types
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, pool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import settings
from src.main import app
from src.models.cliente import Cliente
from src.models.conversacion import Conversacion
from src.models.mensaje import Mensaje
from src.whatsapp.client import WhatsAppClient

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Define TEST_DATABASE_URL con una base migrada exclusiva para pruebas.",
)


def _firmar(cuerpo: bytes) -> str:
    secreto = settings.whatsapp_app_secret.get_secret_value().encode()
    firma = hmac.new(secreto, cuerpo, hashlib.sha256).hexdigest()
    return f"sha256={firma}"


def test_webhook_duplicado_guarda_un_solo_mensaje(monkeypatch: pytest.MonkeyPatch):
    """Meta puede reintentar el mismo payload sin volver a procesarlo."""
    assert TEST_DATABASE_URL is not None
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=pool.NullPool)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    modulo_database = types.ModuleType("src.database")
    modulo_database.session_factory = session_factory
    monkeypatch.setitem(sys.modules, "src.database", modulo_database)

    envios: list[tuple[str, dict]] = []

    async def enviar_interactivo_falso(
        _cliente: WhatsAppClient, destinatario: str, interactivo: dict
    ) -> str:
        envios.append((destinatario, interactivo))
        return "wamid.echo-prueba"

    monkeypatch.setattr(WhatsAppClient, "enviar_interactivo", enviar_interactivo_falso)

    telefono = f"521477{uuid4().int % 10_000_000:07d}"
    whatsapp_message_id = f"wamid.prueba-{uuid4()}"
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "contacts": [
                                {
                                    "wa_id": telefono,
                                    "profile": {"name": "Cliente de prueba"},
                                }
                            ],
                            "messages": [
                                {
                                    "id": whatsapp_message_id,
                                    "from": telefono,
                                    "type": "text",
                                    "text": {"body": "Hola"},
                                }
                            ],
                        }
                    }
                ]
            }
        ]
    }
    cuerpo = json.dumps(payload).encode()
    consulta = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": f"wamid.consulta-{uuid4()}",
                                    "from": telefono,
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {
                                            "id": "consultar",
                                            "title": "Consultar pedido",
                                        },
                                    },
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    cuerpo_consulta = json.dumps(consulta).encode()

    with TestClient(app) as client:
        primera_respuesta = client.post(
            "/webhook/whatsapp",
            content=cuerpo,
            headers={"X-Hub-Signature-256": _firmar(cuerpo)},
        )
        segunda_respuesta = client.post(
            "/webhook/whatsapp",
            content=cuerpo,
            headers={"X-Hub-Signature-256": _firmar(cuerpo)},
        )
        respuesta_consulta = client.post(
            "/webhook/whatsapp",
            content=cuerpo_consulta,
            headers={"X-Hub-Signature-256": _firmar(cuerpo_consulta)},
        )

    async def revisar_base() -> tuple[int, str]:
        async with session_factory() as session:
            conteo = await session.exec(
                select(func.count())
                .select_from(Mensaje)
                .where(Mensaje.whatsapp_message_id == whatsapp_message_id)
            )
            conversacion = await session.exec(
                select(Conversacion)
                .join(Cliente)
                .where(Cliente.telefono == f"+{telefono}")
            )
            return conteo.one(), conversacion.one().estado_actual

    async def limpiar_base() -> None:
        async with session_factory() as session:
            cliente = (
                await session.exec(
                    select(Cliente).where(Cliente.telefono == f"+{telefono}")
                )
            ).first()
            if cliente is None:
                return
            await session.exec(delete(Mensaje).where(Mensaje.cliente_id == cliente.id))
            await session.exec(
                delete(Conversacion).where(Conversacion.cliente_id == cliente.id)
            )
            await session.exec(delete(Cliente).where(Cliente.id == cliente.id))
            await session.commit()

    try:
        assert primera_respuesta.status_code == 200
        assert segunda_respuesta.status_code == 200
        assert respuesta_consulta.status_code == 200
        assert asyncio.run(revisar_base()) == (1, "MENU_PRINCIPAL")
        assert len(envios) == 2
        assert envios[0][0] == telefono
        assert "Soy el asistente" in envios[0][1]["body"]["text"]
        assert len(envios[0][1]["action"]["buttons"]) == 3
        assert "No tienes pedidos activos" in envios[1][1]["body"]["text"]
    finally:
        asyncio.run(limpiar_base())
        asyncio.run(engine.dispose())
