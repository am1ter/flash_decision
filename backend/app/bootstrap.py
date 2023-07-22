from __future__ import annotations

from collections.abc import Callable
from contextlib import _AsyncGeneratorContextManager, suppress
from typing import TYPE_CHECKING

import structlog
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import AsyncConnection

from app.domain.session_provider import (
    Provider,
    ProviderAlphaVantageCrypto,
    ProviderAlphaVantageStocks,
)
from app.infrastructure.cache.redis import CacheRedis
from app.infrastructure.nosql import DbNoSql, DbNoSqlMongo
from app.infrastructure.orm.mapper import init_orm_mappers
from app.infrastructure.sql import DbSql, DbSqlPg
from app.system.config import Settings
from app.system.logger import configure_logger
from app.system.metaclasses import SingletonMeta

if TYPE_CHECKING:
    from app.infrastructure.cache.base import Cache


# Create logger
logger = structlog.get_logger()


AsyncDbConnFactory = Callable[..., _AsyncGeneratorContextManager[AsyncConnection]]


class Bootstrap(metaclass=SingletonMeta):
    """
    Configure the app during the ititialization.
    Singleton is used, because only one instance of bootstrap is allowed.
    """

    db_sql: DbSql
    db_nosql: DbNoSql
    cache: Cache
    provider_stocks: Provider
    provider_crypto: Provider

    def __init__(
        self,
        *,
        start_orm: bool = True,
        db_sql: DbSql = DbSqlPg(),
        db_nosql: DbNoSql = DbNoSqlMongo(),
        cache: Cache = CacheRedis(),
        provider_stocks: Provider = ProviderAlphaVantageStocks(),
        provider_crypto: Provider = ProviderAlphaVantageCrypto(),
    ) -> None:
        # Configure logger
        configure_logger()

        # Set SQL db and map domain models with ORM
        if start_orm:
            with suppress(ArgumentError):
                init_orm_mappers()
        self.db_sql = db_sql
        logger.info(
            "Connection to the SQL database established",
            start_orm=start_orm,
            sql_url=Settings().sql.SQL_URL_WO_PASS,
            sql_schema=Settings().sql.SQL_DB_SCHEMA,
        )

        # Set NoSQL db
        self.db_nosql = db_nosql
        logger.info(
            "Connection to the NoSQL database established",
            start_orm=start_orm,
            sql_url=Settings().nosql.NOSQL_URL,
        )

        # Set cache
        self.cache = cache
        logger.info("Connection to the Cache established", cache=cache.__class__.__name__)

        # Set providers
        self.provider_stocks = provider_stocks
        self.provider_crypto = provider_crypto
        logger.info(
            "Connection to Providers established",
            provider_stocks=provider_stocks.__class__.__name__,
            provider_crypto=provider_crypto.__class__.__name__,
        )
