from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import settings

# El engine conoce cómo abrir conexiones, pero no abre una hasta que una sesión
# ejecuta una consulta. pool_pre_ping evita reutilizar una conexión que Postgres
# cerró mientras la aplicación estaba inactiva.
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
)

# La fábrica es reutilizable; cada request obtiene su propia AsyncSession.
# expire_on_commit=False conserva los atributos de un modelo después de guardar,
# evitando una consulta sorpresa cuando FastAPI construye la respuesta.
session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Entrega una sesión aislada y la cierra al terminar el request."""
    async with session_factory() as session:
        yield session
