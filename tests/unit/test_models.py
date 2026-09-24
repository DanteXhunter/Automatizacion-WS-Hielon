from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import configure_mappers
from sqlmodel import SQLModel

from src.models import (
    Cliente,
    Conversacion,
    Direccion,
    DireccionMensaje,
    EstadoPedido,
    Mensaje,
    Pedido,
    PedidoItem,
    Producto,
)


def test_las_siete_tablas_quedan_registradas_en_metadata():
    tablas_esperadas = {
        "clientes",
        "direcciones",
        "productos",
        "pedidos",
        "pedido_items",
        "conversaciones",
        "mensajes",
    }

    assert tablas_esperadas <= set(SQLModel.metadata.tables)


def test_indices_y_unicidad_criticos_estan_declarados():
    clientes = SQLModel.metadata.tables["clientes"]
    pedidos = SQLModel.metadata.tables["pedidos"]
    conversaciones = SQLModel.metadata.tables["conversaciones"]
    mensajes = SQLModel.metadata.tables["mensajes"]

    assert clientes.c.telefono.unique is True
    assert pedidos.c.numero_orden.unique is True
    assert conversaciones.c.cliente_id.unique is True
    assert mensajes.c.whatsapp_message_id.unique is True
    assert any(
        tuple(indice.columns.keys()) == ("cliente_id", "estado")
        for indice in pedidos.indexes
    )


def test_columnas_postgres_especificas_usan_los_tipos_correctos():
    conversaciones = SQLModel.metadata.tables["conversaciones"]
    pedidos = SQLModel.metadata.tables["pedidos"]
    mensajes = SQLModel.metadata.tables["mensajes"]

    assert isinstance(conversaciones.c.contexto.type, JSONB)
    assert isinstance(pedidos.c.estado.type, SqlEnum)
    assert isinstance(mensajes.c.direccion.type, SqlEnum)
    assert pedidos.c.estado.type.enums == [estado.value for estado in EstadoPedido]
    assert mensajes.c.direccion.type.enums == [
        direccion.value for direccion in DireccionMensaje
    ]


def test_relaciones_bidireccionales_se_pueden_configurar():
    configure_mappers()

    assert Cliente.__mapper__.relationships["direcciones"].back_populates == "cliente"
    assert Direccion.__mapper__.relationships["pedidos"].back_populates == "direccion"
    assert (
        Producto.__mapper__.relationships["pedido_items"].back_populates == "producto"
    )
    assert Pedido.__mapper__.relationships["items"].back_populates == "pedido"
    assert PedidoItem.__mapper__.relationships["pedido"].back_populates == "items"
    assert (
        Conversacion.__mapper__.relationships["cliente"].back_populates
        == "conversacion"
    )
    assert Mensaje.__mapper__.relationships["pedido"].back_populates == "mensajes"
