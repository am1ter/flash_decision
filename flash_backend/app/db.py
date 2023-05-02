from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


def get_new_engine() -> AsyncEngine:
    engine = create_async_engine(settings.DB_URL, echo=settings.LOG_DB_ACCESS)
    return engine


@asynccontextmanager
async def get_connection(engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, Any]:
    conn = await engine.connect()
    try:
        yield conn
    finally:
        await conn.close()


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Give db session using single app-related db engine.
    The name `get_session` cannot be used, because the term `session` is already used inside app.
    """
    async with AsyncSessionFactory() as session:
        yield session


meta = MetaData()
engine = get_new_engine()
AsyncSessionFactory = sessionmaker(  # type: ignore[call-overload]
    bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)
