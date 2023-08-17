import contextlib
from abc import ABCMeta, abstractmethod
from asyncio import TaskGroup
from decimal import Decimal
from typing import Any, assert_never
from uuid import UUID

import pandas as pd
import structlog
from attrs import define

from app.bootstrap import Bootstrap
from app.domain.cache import Cache
from app.domain.repository import RepositorySession
from app.domain.session import (
    DomainSession,
    DomainSessionBlitz,
    DomainSessionClassic,
    DomainSessionCrypto,
    DomainSessionCustom,
    SessionOptions,
    SessionQuotes,
)
from app.domain.session_provider import Provider
from app.domain.session_result import SessionResult
from app.domain.session_user_summary import UserModeSummary
from app.domain.unit_of_work import UnitOfWork
from app.domain.user import DomainUser
from app.services.base import Service
from app.system.config import Settings
from app.system.constants import SessionMode, TickerType
from app.system.exceptions import (
    CacheConnectionError,
    CacheObjectNotFoundError,
    NoUserModeSummaryError,
    SessionAccessError,
)

# Create logger
logger = structlog.get_logger()


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


@define(kw_only=False, slots=False, hash=True)
class ServiceSession(Service):
    """
    Session is the key object of the application.
    This service determine how user interacts with it.
    All interactions are decomposed into commands that called from this service.
    """

    uow: UnitOfWork[RepositorySession]
    cache: Cache | None = Bootstrap().cache if Settings().cache.CACHE_ENABLED else None
    provider_stocks: Provider = Bootstrap().provider_stocks
    provider_crypto: Provider = Bootstrap().provider_crypto

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

    async def calc_session_result(self, session: DomainSession) -> SessionResult:
        result = SessionResult.create(session)
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, result=result)
        return result

    async def calc_user_mode_summary(
        self, user: DomainUser, mode: SessionMode
    ) -> UserModeSummary | None:
        user_mode_summary = await CommandCalcUserModeSummary(self, user, mode).execute()
        await logger.ainfo_finish(
            cls=self.__class__, show_func_name=True, mode=mode, user_score_summary=user_mode_summary
        )
        return user_mode_summary


class Command(metaclass=ABCMeta):
    @abstractmethod
    def execute(self) -> Any:
        pass


@define
class CommandLoadTickers(Command):
    service: ServiceSession

    async def execute(self) -> SessionOptions:
        tickers_col_stocks = await self.service.provider_stocks.get_tickers()
        tickers_col_crypto = await self.service.provider_crypto.get_tickers()
        all_ticker = list(tickers_col_stocks.values()) + list(tickers_col_crypto.values())
        options = SessionOptions(all_ticker=all_ticker)
        return options


@define
class CommandValidateTickers(Command):
    service: ServiceSession

    async def execute(self) -> None:
        is_tickers_stocks_loaded = self.service.provider_stocks.is_tickers_loaded()
        is_tickers_crypto_loaded = self.service.provider_crypto.is_tickers_loaded()
        if not any((is_tickers_stocks_loaded, is_tickers_crypto_loaded)):
            await CommandLoadTickers(service=self.service).execute()


@define
class CommandCreateSession(Command):
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
class CommandLoadQuotes(Command):
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
class CommandSaveSessionToDb(Command):
    service: ServiceSession
    session: DomainSession

    async def execute(self) -> None:
        async with self.service.uow:
            self.service.uow.repository.add(self.session)
            await self.service.uow.commit()


@define
class CommandGetSession(Command):
    service: ServiceSession
    session_id: UUID

    async def execute(self) -> DomainSession:
        async with self.service.uow:
            session = await self.service.uow.repository.get_by_id(self.session_id)
        return session


@define
class CommandCalcUserModeSummary(Command):
    service: ServiceSession
    user: DomainUser
    mode: SessionMode

    async def execute(self) -> UserModeSummary | None:
        async with self.service.uow:
            sessions = await self.service.uow.repository.get_all_sessions_by_user(self.user)
        try:
            user_mode_summary = UserModeSummary.create(sessions, self.mode)
        except NoUserModeSummaryError:
            user_mode_summary = None
        return user_mode_summary


def _find_provider(ticker_type: str) -> Provider:
    match TickerType(ticker_type):
        case TickerType.crypto:
            provider = Bootstrap().provider_crypto
        case _:
            provider = Bootstrap().provider_stocks
    return provider
