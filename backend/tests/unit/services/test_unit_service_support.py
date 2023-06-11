from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any
from unittest import IsolatedAsyncioTestCase

from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from app.bootstrap import Bootstrap
from app.services.support import ServiceSupport


@asynccontextmanager
async def temporal_db_connection() -> AsyncGenerator[AsyncConnection, Any]:
    engine = create_async_engine("sqlite+aiosqlite://")
    conn = await engine.connect()
    try:
        yield conn
    finally:
        await conn.close()


class TestServiceUser(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        bootstrap = Bootstrap(start_orm=True, db_conn_factory=temporal_db_connection)
        self.service = ServiceSupport(bootstrap.db_conn_factory)

    async def test_check_db_connection(self) -> None:
        result = await self.service.check_db_connection()
        self.assertTrue(result)
