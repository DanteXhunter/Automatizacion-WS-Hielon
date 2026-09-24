"""Consultas operativas y cierre controlado del handoff humano."""

import hmac
import logging
from datetime import datetime, timezone
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import settings
from src.database import get_session
from src.fsm.states import EstadoConversacion
from src.models.cliente import Cliente
from src.models.conversacion import Conversacion
from src.models.mensaje import Mensaje
from src.services.mensaje_service import registrar_mensaje_saliente
from src.whatsapp.client import WhatsAppAPIError, WhatsAppClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Administración"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]
admin_key_header = APIKeyHeader(
    name="X-Admin-Key",
    scheme_name="Clave administrativa",
    auto_error=False,
)


class ConversacionAdmin(BaseModel):
    id: UUID
    cliente_id: UUID
    cliente_nombre: str | None
    cliente_telefono: str
    estado_actual: str
    ultima_interaccion: datetime
    motivo_handoff: str | None


class MensajeAdmin(BaseModel):
    id: UUID
    direccion: str
    tipo: str
    contenido: dict[str, Any]
    estado: str | None
    created_at: datetime


class HistorialAdmin(BaseModel):
    conversacion_id: UUID
    offset: int
    limit: int
    mensajes: list[MensajeAdmin]


class CierreHandoff(BaseModel):
    conversacion_id: UUID
    estado_anterior: str
    estado_actual: str
    aviso_enviado: bool


def requerir_clave_admin(
    x_admin_key: Annotated[str | None, Depends(admin_key_header)] = None,
) -> None:
    """Rechaza accesos administrativos sin la clave compartida configurada."""
    secreto = settings.admin_api_key
    esperado = secreto.get_secret_value() if secreto is not None else ""
    if (
        not x_admin_key
        or not esperado
        or not hmac.compare_digest(x_admin_key, esperado)
    ):
        raise HTTPException(status_code=401, detail="Clave administrativa inválida")


AdminAuth = Annotated[None, Depends(requerir_clave_admin)]


@router.get("/conversaciones", response_model=list[ConversacionAdmin])
async def listar_conversaciones(
    _autorizado: AdminAuth,
    session: SessionDep,
    estado: Annotated[EstadoConversacion | None, Query()] = None,
) -> list[ConversacionAdmin]:
    """Lista conversaciones y permite aislar las que esperan un asesor."""
    consulta = (
        select(Conversacion, Cliente)
        .join(Cliente, Cliente.id == Conversacion.cliente_id)
        .order_by(Conversacion.ultima_interaccion.desc())
    )
    if estado is not None:
        consulta = consulta.where(Conversacion.estado_actual == estado.value)

    filas = (await session.exec(consulta)).all()
    return [
        ConversacionAdmin(
            id=conversacion.id,
            cliente_id=cliente.id,
            cliente_nombre=cliente.nombre,
            cliente_telefono=cliente.telefono,
            estado_actual=conversacion.estado_actual,
            ultima_interaccion=conversacion.ultima_interaccion,
            motivo_handoff=conversacion.contexto.get("handoff_motivo"),
        )
        for conversacion, cliente in filas
    ]


@router.get("/conversaciones/{conversacion_id}/mensajes", response_model=HistorialAdmin)
async def consultar_historial(
    conversacion_id: UUID,
    _autorizado: AdminAuth,
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> HistorialAdmin:
    """Devuelve una página del historial en orden cronológico estable."""
    conversacion = (
        await session.exec(
            select(Conversacion).where(Conversacion.id == conversacion_id)
        )
    ).first()
    if conversacion is None:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    mensajes = (
        await session.exec(
            select(Mensaje)
            .where(Mensaje.cliente_id == conversacion.cliente_id)
            .order_by(Mensaje.created_at.asc(), Mensaje.id.asc())
            .offset(offset)
            .limit(limit)
        )
    ).all()
    return HistorialAdmin(
        conversacion_id=conversacion.id,
        offset=offset,
        limit=limit,
        mensajes=[
            MensajeAdmin(
                id=mensaje.id,
                direccion=mensaje.direccion.value,
                tipo=mensaje.tipo,
                contenido=mensaje.contenido,
                estado=mensaje.estado,
                created_at=mensaje.created_at,
            )
            for mensaje in mensajes
        ],
    )


@router.post(
    "/conversaciones/{conversacion_id}/cerrar-handoff", response_model=CierreHandoff
)
async def cerrar_handoff(
    conversacion_id: UUID,
    request: Request,
    _autorizado: AdminAuth,
    session: SessionDep,
) -> CierreHandoff:
    """Devuelve una conversación específica al bot y avisa al cliente."""
    conversacion = (
        await session.exec(
            select(Conversacion)
            .where(Conversacion.id == conversacion_id)
            .with_for_update()
        )
    ).first()
    if conversacion is None:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    if conversacion.estado_actual != EstadoConversacion.EN_ASESOR_HUMANO.value:
        raise HTTPException(
            status_code=409, detail="La conversación no está en handoff"
        )

    cliente = (
        await session.exec(select(Cliente).where(Cliente.id == conversacion.cliente_id))
    ).first()
    if cliente is None:
        raise HTTPException(status_code=409, detail="La conversación no tiene cliente")

    estado_anterior = conversacion.estado_actual
    conversacion.estado_anterior = estado_anterior
    conversacion.estado_actual = EstadoConversacion.IDLE.value
    conversacion.contexto = {}
    conversacion.ultima_interaccion = datetime.now(timezone.utc)
    await session.commit()

    aviso = "El asesor terminó la atención. El bot está disponible nuevamente."
    aviso_enviado = False
    cliente_whatsapp: WhatsAppClient = request.app.state.whatsapp_client
    try:
        message_id = await cliente_whatsapp.enviar_texto(
            cliente.telefono.removeprefix("+"),
            aviso,
        )
        aviso_enviado = True
    except WhatsAppAPIError:
        logger.exception(
            "El handoff se cerró, pero no se pudo avisar al cliente_id=%s",
            cliente.id,
        )

    if aviso_enviado:
        try:
            await registrar_mensaje_saliente(
                session,
                cliente_id=cliente.id,
                whatsapp_message_id=message_id,
                tipo="text",
                contenido={"text": {"body": aviso}},
                pricing_category="service",
                costo_estimado=settings.tarifa_service_mxn,
            )
        except Exception:
            logger.exception(
                "El aviso de cierre se envió, pero no se registró | cliente_id=%s",
                cliente.id,
            )

    return CierreHandoff(
        conversacion_id=conversacion.id,
        estado_anterior=estado_anterior,
        estado_actual=conversacion.estado_actual,
        aviso_enviado=aviso_enviado,
    )
