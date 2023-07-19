from abc import ABCMeta, abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.system.config import Settings


class DbSql(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.engine = self.get_new_engine()

    @abstractmethod
    def get_new_engine(self) -> AsyncEngine:
        pass

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncConnection, Any]:
        """
        Create connection with a new engine or with the default engine if new engine is not set up.
        Could be used for custom SQL code.
        """
        conn = await self.engine.connect()
        try:
            yield conn
        finally:
            await conn.close()

    def get_sessionmaker(self) -> sessionmaker:
        """Create session factory with an engine"""
        async_sessionmaker = sessionmaker(  # type: ignore[call-overload]
            bind=self.engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
        )
        return async_sessionmaker


class DbSqlPg(DbSql):
    def get_new_engine(self) -> AsyncEngine:
        return create_async_engine(Settings().sql.SQL_URL, echo=Settings().log.LOG_SQL_ACCESS)
