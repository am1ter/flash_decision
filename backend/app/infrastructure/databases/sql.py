from abc import ABCMeta
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.domain.db import Db
from app.system.config import Settings


class DbSql(Db, metaclass=ABCMeta):
    """
    ABC class for describing all classical SQL RMDBS.
    Used SQLAlchemy's async engines.
    """

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncConnection, Any]:
        """Create connection with an encapsulated engine. Could be used for custom SQL code."""
        conn = await self.engine.connect()
        try:
            yield conn
        finally:
            await conn.close()

    def get_session(self) -> AsyncSession:
        """Create a session with an encapsulated engine and async sessionmaker"""
        sessionmaker = async_sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        return sessionmaker()


class DbSqlPg(DbSql):
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(Settings().sql.SQL_URL, echo=Settings().log.LOG_SQL_ACCESS)

    async def healthcheck(self) -> bool:
        """Run self healthcheck"""
        try:
            async with self.get_connection() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception:  # noqa: BLE001
            check_result = False
        else:
            check_result = True
        return check_result
