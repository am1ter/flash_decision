from __future__ import annotations

from collections.abc import Callable
from contextlib import _AsyncGeneratorContextManager, suppress

from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.orm import sessionmaker

from app.domain.session_provider import (
    Provider,
    ProviderAlphaVantageCrypto,
    ProviderAlphaVantageStocks,
)
from app.infrastructure.db import AsyncSessionFactory, get_connection
from app.infrastructure.orm.mapper import init_orm_mappers
from app.system.metaclasses import SingletonMeta

AsyncDbConnFactory = Callable[..., _AsyncGeneratorContextManager[AsyncConnection]]


class Bootstrap(metaclass=SingletonMeta):
    """
    Configure the app during the ititialization.
    Singleton is used, because only one instance of bootstrap is allowed.
    """

    db_conn_factory: AsyncDbConnFactory
    db_session_factory: sessionmaker
    provider_stocks: Provider
    provider_crypto: Provider

    def __init__(
        self,
        *,
        start_orm: bool = True,
        db_conn_factory: AsyncDbConnFactory = get_connection,
        db_session_factory: sessionmaker = AsyncSessionFactory,
        provider_stocks: Provider = ProviderAlphaVantageStocks(),
        provider_crypto: Provider = ProviderAlphaVantageCrypto(),
    ) -> None:
        # Mapping Domain models with ORM
        if start_orm:
            with suppress(ArgumentError):
                init_orm_mappers()

        # Set db-related factories
        self.db_conn_factory = db_conn_factory
        self.db_session_factory = db_session_factory

        # Set providers and download ticker list for all data provider
        if provider_stocks:
            self.provider_stocks = provider_stocks
            self.provider_stocks.get_tickers()
        if provider_crypto:
            self.provider_crypto = provider_crypto
            self.provider_crypto.get_tickers()
