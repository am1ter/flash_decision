from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.system.config import settings


def get_new_engine() -> AsyncEngine:
    engine = create_async_engine(settings.DB_URL, echo=settings.LOG_DB_ACCESS)
    return engine


engine = get_new_engine()


@asynccontextmanager
async def get_connection(engine: AsyncEngine = engine) -> AsyncGenerator[AsyncConnection, Any]:
    """
    Create connection with a new engine or with the default engine if new engine is not set up.
    Could be used for custom SQL code.
    """
    conn = await engine.connect()
    try:
        yield conn
    finally:
        await conn.close()


def get_sessionmaker(engine: AsyncEngine = engine) -> sessionmaker:
    """
    Create session factory with a new engine or with the default engine if new engine is not set up.
    Could be used in the case, when you need to use multiple engines.
    """
    async_sessionmaker = sessionmaker(  # type: ignore[call-overload]
        bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
    )
    return async_sessionmaker


AsyncSessionFactory = get_sessionmaker()


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Give db session using single app-related db engine.
    The name `get_session` cannot be used, because the term `session` is already used inside app.
    """
    async with AsyncSessionFactory() as session:
        yield session


DbDep = Annotated[AsyncSession, Depends(get_db)]
