from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.bootstrap import Bootstrap
from app.infrastructure.databases.sql import DbSql
from tests.unit.mock_session_providers import (
    provider_av_crypto_mock_success,
    provider_av_stocks_mock_success,
)


class DbSqlFake(DbSql):
    def get_engine(self) -> AsyncEngine:
        return create_async_engine("sqlite+aiosqlite://")

    async def healthcheck(self) -> bool:
        return True


type(Bootstrap)._instances = {}
Bootstrap(
    start_orm=True,
    db_sql=DbSqlFake(),
    db_nosql=None,  # type: ignore[arg-type]
    cache=None,  # type: ignore[arg-type]
    provider_stocks=provider_av_stocks_mock_success,
    provider_crypto=provider_av_crypto_mock_success,
)
