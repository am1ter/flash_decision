import contextlib
from typing import Annotated, assert_never

from attr import define
from fastapi import Depends

from app.api.schemas.session import ReqSession
from app.bootstrap import Bootstrap
from app.domain.session import (
    DomainSession,
    DomainSessionBlitz,
    DomainSessionClassic,
    DomainSessionCrypto,
    DomainSessionCustom,
    SessionOptions,
)
from app.domain.session_provider import Provider, Ticker, csv_table
from app.domain.user import DomainUser
from app.infrastructure.repositories.session import RepositorySessionSQL
from app.infrastructure.units_of_work.base_sql import UnitOfWorkSQLAlchemy
from app.system.config import settings
from app.system.constants import SessionMode, TickerType
from app.system.exceptions import (
    CacheConnectionError,
    CacheObjectNotFoundError,
    MemoryObjectNotFoundError,
)
from app.system.logger import create_logger

# Create logger
logger = create_logger("backend.service.session")

# Internal dependencies
uow_session = UnitOfWorkSQLAlchemy(repository_type=RepositorySessionSQL, create_task_group=True)
UowSessionDep = Annotated[UnitOfWorkSQLAlchemy, Depends(uow_session)]


@define
class TickersColRaw:
    stocks: csv_table
    crypto: csv_table


@define
class TickersColProcessed:
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
        self.cache = Bootstrap().cache if settings.CACHE_ENABLED else None
        self.provider_stocks = Bootstrap().provider_stocks
        self.provider_crypto = Bootstrap().provider_crypto

    async def collect_session_options(self) -> SessionOptions:
        all_tickers = await CommandLoadTickers(self).execute()
        options = SessionOptions(all_ticker=all_tickers)
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True)
        return options

    async def start_session(
        self, mode: SessionMode, session_params: ReqSession | None, user: DomainUser
    ) -> DomainSession:
        await CommandValidateTickers(self).execute()
        session = CommandCreateSession(self, mode, session_params, user).execute()
        await CommandStartSession(self, session).execute()
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, session=session)
        return session


@define
class CommandLoadTickers:
    service: ServiceSession

    async def execute(self) -> list[Ticker]:
        tickers_col_proc = await self._load_processed_tickers()
        return list(tickers_col_proc.stocks.values()) + list(tickers_col_proc.crypto.values())

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
    session_params: ReqSession | None
    user: DomainUser

    def execute(self) -> DomainSession:
        session = self._create_session()
        session.bound_to_user(self.user)
        return session

    def _find_provider(self, ticker_type: str) -> Provider:
        match TickerType(ticker_type):
            case TickerType.crypto:
                provider = self.service.provider_crypto
            case _:
                provider = self.service.provider_stocks
        return provider

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
                    provider=self._find_provider(self.session_params.ticker_type),
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
class CommandStartSession:
    service: ServiceSession
    session: DomainSession

    async def execute(self) -> DomainSession:
        try:
            async with self.service.uow:
                self.service.uow.task_group.create_task(self.session.start())
                self.service.uow.repository.add(self.session)
                self.service.uow.task_group.create_task(self.service.uow.commit())
        except ExceptionGroup as eg:
            raise eg.exceptions[0] from eg
        return self.session
