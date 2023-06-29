from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from app.bootstrap import Bootstrap
from app.services.support import ServiceSupport

pytestmark = pytest.mark.asyncio


@asynccontextmanager
async def fake_db_connection() -> AsyncGenerator[AsyncConnection, Any]:
    engine = create_async_engine("sqlite+aiosqlite://")
    conn = await engine.connect()
    try:
        yield conn
    finally:
        await conn.close()


@pytest.fixture()
def service_support() -> ServiceSupport:
    Bootstrap(start_orm=True, db_conn_factory=fake_db_connection)
    return ServiceSupport()


class TestServiceSupport:
    async def test_check_db_connection(self, service_support: ServiceSupport) -> None:
        result = await service_support.check_db_connection()
        assert result
