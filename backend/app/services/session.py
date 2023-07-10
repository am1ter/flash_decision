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
    Session is the key object of the application. This service determine how user interacts with it.
    """

    def __init__(self, uow: UowSessionDep) -> None:
        self.uow = uow
        self.cache = Bootstrap().cache if settings.CACHE_ENABLED else None
        self.provider_stocks = Bootstrap().provider_stocks
        self.provider_crypto = Bootstrap().provider_crypto
        # Cache keys names
        self.ck_tickers_stocks = f"{self.provider_stocks.__class__.__name__}:_tickers"
        self.ck_tickers_crypto = f"{self.provider_crypto.__class__.__name__}:_tickers"

    def _get_processed_tickers_from_memory(self) -> TickersColProcessed:
        return TickersColProcessed(
            stocks=self.provider_stocks.get_tickers(),
            crypto=self.provider_crypto.get_tickers(),
        )

    async def _get_raw_tickers_from_cache(self) -> TickersColRaw:
        if not self.cache:
            raise CacheObjectNotFoundError
        raw_tickers = await self.cache.mget([self.ck_tickers_stocks, self.ck_tickers_crypto])
        assert isinstance(raw_tickers[0], list) and isinstance(raw_tickers[1], list)
        return TickersColRaw(stocks=raw_tickers[0], crypto=raw_tickers[1])

    async def _get_raw_tickers_from_provider(self) -> TickersColRaw:
        tickers_col_raw = TickersColRaw(
            stocks=await self.provider_stocks.download_raw_tickers(),
            crypto=await self.provider_crypto.download_raw_tickers(),
        )
        if self.cache:
            objects_to_cache = {
                self.ck_tickers_stocks: tickers_col_raw.stocks,
                self.ck_tickers_crypto: tickers_col_raw.crypto,
            }
            with contextlib.suppress(CacheConnectionError):
                await self.cache.mset(objects_to_cache)
        return tickers_col_raw

    async def _load_tickers(self) -> TickersColProcessed:
        with contextlib.suppress(MemoryObjectNotFoundError):
            return self._get_processed_tickers_from_memory()

        try:
            tickers_col_raw = await self._get_raw_tickers_from_cache()
        except (CacheObjectNotFoundError, CacheConnectionError):
            tickers_col_raw = await self._get_raw_tickers_from_provider()

        return TickersColProcessed(
            self.provider_stocks.process_tickers(tickers_col_raw.stocks),
            self.provider_crypto.process_tickers(tickers_col_raw.crypto),
        )

    async def collect_session_options(self) -> SessionOptions:
        tickers_col_proc = await self._load_tickers()
        all_ticker = list(tickers_col_proc.stocks.values()) + list(tickers_col_proc.crypto.values())
        options = SessionOptions(all_ticker=all_ticker)
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True)
        return options

    def _find_provider(self, ticker_type: str) -> Provider:
        match TickerType(ticker_type):
            case TickerType.crypto:
                provider = self.provider_crypto
            case _:
                provider = self.provider_stocks
        return provider

    def _create_session(
        self, mode: SessionMode, session_params: ReqSession | None
    ) -> DomainSession:
        session: DomainSession
        match mode:
            case SessionMode.classic:
                session = DomainSessionClassic.create(provider=self.provider_stocks)
            case SessionMode.blitz:
                session = DomainSessionBlitz.create(provider=self.provider_stocks)
            case SessionMode.crypto:
                session = DomainSessionCrypto.create(provider=self.provider_crypto)
            case SessionMode.custom:
                assert session_params
                session = DomainSessionCustom.create(
                    provider=self._find_provider(session_params.ticker_type),
                    ticker_symbol=session_params.ticker_symbol,
                    timeframe=session_params.timeframe,
                    barsnumber=session_params.barsnumber,
                    timelimit=session_params.timelimit,
                    iterations=session_params.iterations,
                    slippage=session_params.slippage,
                    fixingbar=session_params.fixingbar,
                )
            case _:
                assert_never(mode)
        return session

    async def start_session(
        self, mode: SessionMode, session_params: ReqSession | None, user: DomainUser
    ) -> DomainSession:
        # Validate if provider contains information about tickers
        await self._load_tickers()
        # Create session
        session = self._create_session(mode, session_params)
        # Link to user
        session.bound_to_user(user)
        # Start session
        try:
            async with self.uow:
                self.uow.task_group.create_task(session.start())
                self.uow.repository.add(session)
                self.uow.task_group.create_task(self.uow.commit())
        except ExceptionGroup as eg:
            raise eg.exceptions[0] from eg
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, session=session)
        return session
