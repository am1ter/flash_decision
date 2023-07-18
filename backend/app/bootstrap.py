from __future__ import annotations

from collections.abc import Callable
from contextlib import _AsyncGeneratorContextManager, suppress
from typing import TYPE_CHECKING

import structlog
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.orm import sessionmaker

from app.domain.session_provider import (
    Provider,
    ProviderAlphaVantageCrypto,
    ProviderAlphaVantageStocks,
)
from app.infrastructure.cache.redis import CacheRedis
from app.infrastructure.db import AsyncSessionFactory, get_connection
from app.infrastructure.orm.mapper import init_orm_mappers
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

    db_conn_factory: AsyncDbConnFactory
    db_session_factory: sessionmaker
    cache: Cache
    provider_stocks: Provider
    provider_crypto: Provider

    def __init__(
        self,
        *,
        start_orm: bool = True,
        db_conn_factory: AsyncDbConnFactory = get_connection,
        db_session_factory: sessionmaker = AsyncSessionFactory,
        cache: Cache = CacheRedis(),
        provider_stocks: Provider = ProviderAlphaVantageStocks(),
        provider_crypto: Provider = ProviderAlphaVantageCrypto(),
    ) -> None:
        # Configure logger
        configure_logger()

        # Set db-related factories and map domain models with ORM
        if start_orm:
            with suppress(ArgumentError):
                init_orm_mappers()
        self.db_conn_factory = db_conn_factory
        self.db_session_factory = db_session_factory
        logger.info(
            "Connection to db established",
            start_orm=start_orm,
            db_url=Settings().db.DB_URL_WO_PASS,
            db_schema=Settings().db.DB_SCHEMA,
        )

        # Set cache
        self.cache = cache
        logger.info("Connection to cache established", cache=cache.__class__.__name__)

        # Set providers
        self.provider_stocks = provider_stocks
        self.provider_crypto = provider_crypto
        logger.info(
            "Connection to providers established",
            provider_stocks=provider_stocks.__class__.__name__,
            provider_crypto=provider_crypto.__class__.__name__,
        )
