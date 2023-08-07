import contextlib
from asyncio import TaskGroup
from decimal import Decimal
from typing import Annotated, assert_never, cast

import pandas as pd
import structlog
from attrs import define
from fastapi import Depends
from uuid6 import UUID

from app.bootstrap import Bootstrap
from app.domain.session import (
    DomainSession,
    DomainSessionBlitz,
    DomainSessionClassic,
    DomainSessionCrypto,
    DomainSessionCustom,
    SessionOptions,
    SessionQuotes,
)
from app.domain.session_provider import Provider, Ticker, csv_table
from app.domain.user import DomainUser
from app.infrastructure.repositories.session import RepositorySessionSql
from app.infrastructure.units_of_work.base_sql import UnitOfWorkSqlAlchemy
from app.system.config import Settings
from app.system.constants import SessionMode, TickerType
from app.system.exceptions import (
    CacheConnectionError,
    CacheObjectNotFoundError,
    MemoryObjectNotFoundError,
    SessionAccessError,
)

# Create logger
logger = structlog.get_logger()

# Internal dependencies
uow_session = UnitOfWorkSqlAlchemy(repository_type=RepositorySessionSql)
UowSessionDep = Annotated[UnitOfWorkSqlAlchemy, Depends(uow_session)]


@define
class SessionParams:
    """This container must be used in external controllers (e.g. API layer) to create Session"""

    mode: str
    ticker_type: str
    ticker_symbol: str
    timeframe: str
    barsnumber: int
    timelimit: int
    iterations: int
    slippage: Decimal
    fixingbar: int


@define
class TickersColRaw:
    """
    Information about all possible tickers stored in 2 formats: Raw and Processed.
    Raw - exact the same data received from Provider (json-like format).
    """

    stocks: csv_table
    crypto: csv_table


@define
class TickersColProcessed:
    """
    Information about all possible tickers stored in 2 formats: Raw and Processed.
    Processed - the data after serialization json to python objects.
    """

    stocks: dict[str, Ticker]
    crypto: dict[str, Ticker]


class ServiceSession:
    """
    Session is the key object of the application.
    This service determine how user interacts with it.
    All interactions are decomposed into commands that called from this service.
    """

    def __init__(self, uow: UowSessionDep) -> None:
        self.uow = uow
        self.cache = Bootstrap().cache if Settings().cache.CACHE_ENABLED else None
        self.provider_stocks = Bootstrap().provider_stocks
        self.provider_crypto = Bootstrap().provider_crypto

    async def collect_session_options(self) -> SessionOptions:
        options = await CommandLoadTickers(self).execute()
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True)
        return options

    async def create_session(
        self, mode: SessionMode, session_params: SessionParams | None, user: DomainUser
    ) -> SessionQuotes:
        await CommandValidateTickers(self).execute()
        session = CommandCreateSession(self, mode, session_params, user).execute()
        try:
            async with TaskGroup() as task_group:
                session_quotes = task_group.create_task(CommandLoadQuotes(self, session).execute())
                task_group.create_task(CommandSaveSessionToDb(self, session).execute())
        except ExceptionGroup as eg:
            raise eg.exceptions[0] from eg
        session_quotes_result = session_quotes.result()
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True)
        return session_quotes_result

    async def get_session(self, session_id: UUID, user: DomainUser) -> DomainSession:
        session = await CommandGetSession(self, session_id).execute()
        if session.user != user:
            raise SessionAccessError
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, session=session)
        return session


@define
class CommandLoadTickers:
    service: ServiceSession

    async def execute(self) -> SessionOptions:
        tickers_col_proc = await self._load_processed_tickers()
        all_ticker = list(tickers_col_proc.stocks.values()) + list(tickers_col_proc.crypto.values())
        options = SessionOptions(all_ticker=all_ticker)
        return options

    @staticmethod
    def _cache_key_by_provider(provider: Provider) -> str:
        return f"{provider.__class__.__name__}:_tickers"

    def _get_processed_tickers_from_memory(self) -> TickersColProcessed:
        return TickersColProcessed(
            stocks=self.service.provider_stocks.get_tickers(),
            crypto=self.service.provider_crypto.get_tickers(),
        )

    async def _get_raw_tickers_from_cache(self) -> TickersColRaw:
        if not self.service.cache:
            raise CacheObjectNotFoundError
        raw_tickers = await self.service.cache.mget(
            [
                self._cache_key_by_provider(self.service.provider_stocks),
                self._cache_key_by_provider(self.service.provider_crypto),
            ]
        )
        assert isinstance(raw_tickers[0], list) and isinstance(raw_tickers[1], list)
        return TickersColRaw(stocks=raw_tickers[0], crypto=raw_tickers[1])

    async def _get_raw_tickers_from_provider(self) -> TickersColRaw:
        tickers_col_raw = TickersColRaw(
            stocks=await self.service.provider_stocks.download_raw_tickers(),
            crypto=await self.service.provider_crypto.download_raw_tickers(),
        )
        if self.service.cache:
            objects_to_cache = {
                self._cache_key_by_provider(self.service.provider_stocks): tickers_col_raw.stocks,
                self._cache_key_by_provider(self.service.provider_crypto): tickers_col_raw.crypto,
            }
            with contextlib.suppress(CacheConnectionError):
                await self.service.cache.mset(objects_to_cache)
        return tickers_col_raw

    async def _load_processed_tickers(self) -> TickersColProcessed:
        with contextlib.suppress(MemoryObjectNotFoundError):
            return self._get_processed_tickers_from_memory()

        try:
            tickers_col_raw = await self._get_raw_tickers_from_cache()
        except (CacheObjectNotFoundError, CacheConnectionError):
            tickers_col_raw = await self._get_raw_tickers_from_provider()

        return TickersColProcessed(
            self.service.provider_stocks.process_tickers(tickers_col_raw.stocks),
            self.service.provider_crypto.process_tickers(tickers_col_raw.crypto),
        )


@define
class CommandValidateTickers:
    service: ServiceSession

    async def execute(self) -> None:
        try:
            self.service.provider_stocks.get_tickers()
            self.service.provider_crypto.get_tickers()
        except MemoryObjectNotFoundError:
            await CommandLoadTickers(service=self.service).execute()


@define
class CommandCreateSession:
    service: ServiceSession
    mode: SessionMode
    session_params: SessionParams | None
    user: DomainUser

    def execute(self) -> DomainSession:
        session = self._create_session()
        session.bound_to_user(self.user)
        return session

    def _create_session(self) -> DomainSession:
        session: DomainSession
        match self.mode:
            case SessionMode.classic:
                session = DomainSessionClassic.create(provider=self.service.provider_stocks)
            case SessionMode.blitz:
                session = DomainSessionBlitz.create(provider=self.service.provider_stocks)
            case SessionMode.crypto:
                session = DomainSessionCrypto.create(provider=self.service.provider_crypto)
            case SessionMode.custom:
                assert self.session_params
                session = DomainSessionCustom.create(
                    provider=_find_provider(self.session_params.ticker_type),
                    ticker_symbol=self.session_params.ticker_symbol,
                    timeframe=self.session_params.timeframe,
                    barsnumber=self.session_params.barsnumber,
                    timelimit=self.session_params.timelimit,
                    iterations=self.session_params.iterations,
                    slippage=self.session_params.slippage,
                    fixingbar=self.session_params.fixingbar,
                )
            case _:
                assert_never(self.mode)
        return session


@define
class CommandLoadQuotes:
    service: ServiceSession
    session: DomainSession

    async def execute(self) -> SessionQuotes:
        try:
            df_quotes = await self._get_from_cache()
        except (CacheObjectNotFoundError, CacheConnectionError):
            df_quotes = await self._get_from_provider()
        session_quotes = SessionQuotes.create(session=self.session, df_quotes=df_quotes)
        return session_quotes

    @property
    def _cache_key(self) -> str:
        prefix = SessionQuotes.__name__
        return f"{prefix}:{self.session.ticker.symbol}:{self.session.timeframe.value}:quotes"

    async def _get_from_cache(self) -> pd.DataFrame:
        if not self.service.cache:
            raise CacheObjectNotFoundError
        raw_data = await self.service.cache.get(self._cache_key)
        df_quotes = pd.read_json(raw_data)
        return df_quotes

    async def _get_from_provider(self) -> pd.DataFrame:
        provider = _find_provider(self.session.ticker.ticker_type.value)
        df_quotes = await provider.get_data(self.session.ticker, self.session.timeframe)
        if self.service.cache:
            with contextlib.suppress(CacheConnectionError):
                await self.service.cache.set(self._cache_key, df_quotes.to_json())
        return df_quotes


@define
class CommandSaveSessionToDb:
    service: ServiceSession
    session: DomainSession

    async def execute(self) -> None:
        async with self.service.uow:
            self.service.uow.repository.add(self.session)
            await self.service.uow.commit()


@define
class CommandGetSession:
    service: ServiceSession
    session_id: UUID

    async def execute(self) -> DomainSession:
        async with self.service.uow:
            self.service.uow.repository = cast(RepositorySessionSql, self.service.uow.repository)
            session = await self.service.uow.repository.get_by_id(self.session_id)
        return session


def _find_provider(ticker_type: str) -> Provider:
    match TickerType(ticker_type):
        case TickerType.crypto:
            provider = Bootstrap().provider_crypto
        case _:
            provider = Bootstrap().provider_stocks
    return provider
