from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.bootstrap import Bootstrap
from app.infrastructure.sql import DbSql
from tests.conftest import ProviderAVCryptoMockSuccess, ProviderAVStocksMockSuccess


class DbSqlFake(DbSql):
    def get_engine(self) -> AsyncEngine:
        return create_async_engine("sqlite+aiosqlite://")


type(Bootstrap)._instances = {}
Bootstrap(
    start_orm=True,
    db_sql=DbSqlFake(),
    db_nosql=None,  # type: ignore[arg-type]
    cache=None,  # type: ignore[arg-type]
    provider_stocks=ProviderAVStocksMockSuccess(),
    provider_crypto=ProviderAVCryptoMockSuccess(),
)
