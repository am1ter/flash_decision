from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from app.bootstrap import Bootstrap
from tests.conftest import ProviderAVCryptoMockSuccess, ProviderAVStocksMockSuccess


@asynccontextmanager
async def fake_db_connection() -> AsyncGenerator[AsyncConnection, Any]:
    engine = create_async_engine("sqlite+aiosqlite://")
    conn = await engine.connect()
    try:
        yield conn
    finally:
        await conn.close()


Bootstrap(
    start_orm=True,
    db_conn_factory=fake_db_connection,
    provider_stocks=ProviderAVStocksMockSuccess(),
    provider_crypto=ProviderAVCryptoMockSuccess(),
)
