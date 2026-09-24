"""Contrato HTTP de consulta y cierre del handoff."""

import os
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api import admin
from src.fsm.states import EstadoConversacion
from src.main import app
from src.models.cliente import Cliente
from src.models.conversacion import Conversacion
from src.models.mensaje import DireccionMensaje, Mensaje

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
client = TestClient(app)


class Resultado:
    def __init__(self, valores):
        self.valores = list(valores)

    def first(self):
        return self.valores[0] if self.valores else None

    def all(self):
        return self.valores


class SesionSecuencial:
    def __init__(self, *resultados):
        self.resultados = iter(resultados)
        self.commits = 0

    async def exec(self, _consulta):
        return Resultado(next(self.resultados))

    async def commit(self):
        self.commits += 1


def test_clave_admin_rechaza_ausente_o_incorrecta(monkeypatch):
    monkeypatch.setattr(admin.settings, "admin_api_key", SecretStr("clave-correcta"))

    with pytest.raises(HTTPException) as ausente:
        admin.requerir_clave_admin(None)
    with pytest.raises(HTTPException) as incorrecta:
        admin.requerir_clave_admin("otra-clave")

    assert ausente.value.status_code == 401
    assert incorrecta.value.status_code == 401
    assert admin.requerir_clave_admin("clave-correcta") is None


def test_endpoint_admin_sin_header_responde_401(monkeypatch):
    monkeypatch.setattr(admin.settings, "admin_api_key", SecretStr("clave-correcta"))

    respuesta = client.get("/admin/conversaciones")

    assert respuesta.status_code == 401


@pytest.mark.asyncio
async def test_lista_filtrable_incluye_cliente_estado_y_motivo():
    cliente = Cliente(
        id=uuid4(),
        nombre="Restaurante Norte",
        telefono="+5214771234567",
    )
    conversacion = Conversacion(
        id=uuid4(),
        cliente_id=cliente.id,
        estado_actual=EstadoConversacion.EN_ASESOR_HUMANO.value,
        contexto={"handoff_motivo": "Solicitud del cliente"},
    )
    session = SesionSecuencial([(conversacion, cliente)])

    respuesta = await admin.listar_conversaciones(
        None,
        session,
        EstadoConversacion.EN_ASESOR_HUMANO,
    )

    assert len(respuesta) == 1
    assert respuesta[0].cliente_telefono == cliente.telefono
    assert respuesta[0].estado_actual == EstadoConversacion.EN_ASESOR_HUMANO
    assert respuesta[0].motivo_handoff == "Solicitud del cliente"


@pytest.mark.asyncio
async def test_historial_es_paginado_y_conserva_orden_cronologico():
    cliente_id = uuid4()
    conversacion = Conversacion(id=uuid4(), cliente_id=cliente_id)
    primero = Mensaje(
        id=uuid4(),
        cliente_id=cliente_id,
        direccion=DireccionMensaje.ENTRANTE,
        whatsapp_message_id="wamid.1",
        tipo="text",
        contenido={"text": {"body": "Primero"}},
        created_at=datetime.now(timezone.utc),
    )
    segundo = Mensaje(
        id=uuid4(),
        cliente_id=cliente_id,
        direccion=DireccionMensaje.SALIENTE,
        whatsapp_message_id="wamid.2",
        tipo="text",
        contenido={"text": {"body": "Segundo"}},
        created_at=primero.created_at + timedelta(seconds=1),
    )
    session = SesionSecuencial([conversacion], [primero, segundo])

    respuesta = await admin.consultar_historial(
        conversacion.id,
        None,
        session,
        offset=0,
        limit=50,
    )

    assert respuesta.offset == 0
    assert respuesta.limit == 50
    assert [mensaje.contenido["text"]["body"] for mensaje in respuesta.mensajes] == [
        "Primero",
        "Segundo",
    ]


@pytest.mark.asyncio
async def test_cerrar_handoff_solo_cambia_conversacion_y_avisa(monkeypatch):
    cliente = Cliente(id=uuid4(), telefono="+5214771234567")
    conversacion = Conversacion(
        id=uuid4(),
        cliente_id=cliente.id,
        estado_actual=EstadoConversacion.EN_ASESOR_HUMANO.value,
        contexto={"handoff_motivo": "Solicitud del cliente"},
    )
    otra = Conversacion(
        id=uuid4(),
        cliente_id=uuid4(),
        estado_actual=EstadoConversacion.EN_ASESOR_HUMANO.value,
    )
    session = SesionSecuencial([conversacion], [cliente])
    envios = []
    registros = []

    class ClienteWhatsApp:
        async def enviar_texto(self, telefono, texto):
            envios.append((telefono, texto))
            return "wamid.retorno"

    async def registrar(_session, **datos):
        registros.append(datos)

    monkeypatch.setattr(admin, "registrar_mensaje_saliente", registrar)
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(whatsapp_client=ClienteWhatsApp()))
    )

    respuesta = await admin.cerrar_handoff(
        conversacion.id,
        request,
        None,
        session,
    )

    assert respuesta.estado_anterior == EstadoConversacion.EN_ASESOR_HUMANO
    assert respuesta.estado_actual == EstadoConversacion.IDLE
    assert respuesta.aviso_enviado is True
    assert conversacion.contexto == {}
    assert otra.estado_actual == EstadoConversacion.EN_ASESOR_HUMANO
    assert session.commits == 1
    assert envios[0][0] == "5214771234567"
    assert registros[0]["pricing_category"] == "service"


def test_endpoints_admin_aparecen_en_swagger():
    rutas = set(app.openapi()["paths"])

    assert "/admin/conversaciones" in rutas
    assert "/admin/conversaciones/{conversacion_id}/mensajes" in rutas
    assert "/admin/conversaciones/{conversacion_id}/cerrar-handoff" in rutas


@pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Define TEST_DATABASE_URL con una base PostgreSQL migrada para pruebas.",
)
@pytest.mark.asyncio
async def test_consulta_y_cierre_aislado_en_postgresql():
    assert TEST_DATABASE_URL is not None
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=pool.NullPool)
    fabrica = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    cliente = Cliente(telefono="+5214779900101", nombre="Cliente handoff")
    otro_cliente = Cliente(telefono="+5214779900102", nombre="Otro cliente")
    conversacion = Conversacion(
        cliente_id=cliente.id,
        estado_actual=EstadoConversacion.EN_ASESOR_HUMANO.value,
        contexto={"handoff_motivo": "Solicitud del cliente"},
    )
    otra_conversacion = Conversacion(
        cliente_id=otro_cliente.id,
        estado_actual=EstadoConversacion.EN_ASESOR_HUMANO.value,
        contexto={"handoff_motivo": "3 intentos inválidos en el menú"},
    )
    mensaje = Mensaje(
        cliente_id=cliente.id,
        direccion=DireccionMensaje.ENTRANTE,
        whatsapp_message_id="wamid.admin-postgres-entrada",
        tipo="text",
        contenido={"text": {"body": "Necesito ayuda"}},
    )

    class ClienteWhatsApp:
        async def enviar_texto(self, _telefono, _texto):
            return "wamid.admin-postgres-salida"

    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(whatsapp_client=ClienteWhatsApp()))
    )

    try:
        async with fabrica() as session:
            session.add_all(
                [cliente, otro_cliente, conversacion, otra_conversacion, mensaje]
            )
            await session.commit()

            conversaciones = await admin.listar_conversaciones(
                None,
                session,
                EstadoConversacion.EN_ASESOR_HUMANO,
            )
            historial = await admin.consultar_historial(
                conversacion.id,
                None,
                session,
                offset=0,
                limit=1,
            )
            cierre = await admin.cerrar_handoff(
                conversacion.id,
                request,
                None,
                session,
            )

            otra_persistida = (
                await session.exec(
                    select(Conversacion).where(Conversacion.id == otra_conversacion.id)
                )
            ).one()

            assert {fila.id for fila in conversaciones} == {
                conversacion.id,
                otra_conversacion.id,
            }
            assert [item.contenido for item in historial.mensajes] == [
                {"text": {"body": "Necesito ayuda"}}
            ]
            assert cierre.estado_actual == EstadoConversacion.IDLE
            assert otra_persistida.estado_actual == EstadoConversacion.EN_ASESOR_HUMANO
    finally:
        async with fabrica() as session:
            await session.exec(
                delete(Mensaje).where(
                    Mensaje.cliente_id.in_([cliente.id, otro_cliente.id])
                )
            )
            await session.exec(
                delete(Conversacion).where(
                    Conversacion.cliente_id.in_([cliente.id, otro_cliente.id])
                )
            )
            await session.exec(
                delete(Cliente).where(Cliente.id.in_([cliente.id, otro_cliente.id]))
            )
            await session.commit()
        await engine.dispose()
