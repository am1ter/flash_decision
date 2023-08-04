from __future__ import annotations

from abc import ABCMeta, abstractmethod
from random import choice
from typing import TYPE_CHECKING, ClassVar, Self, assert_never

import pandas as pd
from attrs import define, field
from pandas import Timestamp

from app.domain.base import Agregate, field_relationship
from app.domain.session_provider import Provider, Ticker
from app.system.config import Settings
from app.system.constants import (
    SessionBarsnumber,
    SessionFixingbar,
    SessionIterations,
    SessionMode,
    SessionSlippage,
    SessionStatus,
    SessionTimeframe,
    SessionTimelimit,
    SessionTradingType,
)
from app.system.exceptions import (
    MemoryObjectNotFoundError,
    ProviderInvalidDataError,
    SessionConfigurationError,
)
from app.system.metaclasses import SingletonMeta

if TYPE_CHECKING:
    from decimal import Decimal

    from app.domain.decision import DomainDecision
    from app.domain.user import DomainUser


@define(kw_only=True, slots=False, hash=True)
class SessionQuotes:
    """Contains session and quotes dataframe for creating iterations' charts"""

    session: DomainSession
    df_quotes: pd.DataFrame = field(repr=False)
    trading_type: SessionTradingType
    first_bar_datetime: Timestamp = field()
    last_bar_datetime: Timestamp = field()
    total_df_quotes_bars: int = field()
    total_bars_required: int = field()

    @total_bars_required.default
    def _default_total_bars_required(self) -> int:
        one_iter_total_bars = self.session.barsnumber.value + self.session.fixingbar.value
        return one_iter_total_bars * self.session.iterations.value

    @first_bar_datetime.validator
    def _validate_first_bar_datetime(self, attribute: str, value: Timestamp) -> None:
        if value < self.last_bar_datetime:
            raise SessionConfigurationError

    @last_bar_datetime.validator
    def _validate_last_bar_datetime(self, attribute: str, value: Timestamp) -> None:
        if value > self.first_bar_datetime:
            raise SessionConfigurationError

    @total_df_quotes_bars.validator
    def _validate_total_df_quotes_bars(self, attribute: str, value: int) -> None:
        if value < self.total_bars_required:
            raise ProviderInvalidDataError

    @staticmethod
    def _determine_trading_type(
        first_bar_datetime: Timestamp, last_bar_datetime: Timestamp
    ) -> SessionTradingType:
        diff = first_bar_datetime - last_bar_datetime
        for treshold in SessionTradingType:
            if diff.days < treshold.value:
                return treshold
        assert_never(diff)

    @classmethod
    def create(cls, session: DomainSession, df_quotes: pd.DataFrame) -> SessionQuotes:
        first_bar_datetime = df_quotes["datetime"].iloc[0]
        last_bar_datetime = df_quotes["datetime"].iloc[-1]
        trading_type = cls._determine_trading_type(first_bar_datetime, last_bar_datetime)
        total_df_quotes_bars = len(df_quotes)
        session_time_series = cls(
            session=session,
            df_quotes=df_quotes,
            trading_type=trading_type,
            first_bar_datetime=first_bar_datetime,
            last_bar_datetime=last_bar_datetime,
            total_df_quotes_bars=total_df_quotes_bars,
        )
        return session_time_series


@define(kw_only=True, slots=False, hash=True)
class DomainSession(Agregate, metaclass=ABCMeta):
    """
    Session is the key object of the application.
    Class attributes is options which determine most application functions behavior.
    The app has different modes - each of them is a subclass of the Session.
    """

    random_tickers: ClassVar[str]

    mode: SessionMode
    ticker: Ticker = field(converter=lambda j: Ticker(**j) if isinstance(j, dict) else j)
    timeframe: SessionTimeframe
    barsnumber: SessionBarsnumber
    timelimit: SessionTimelimit
    iterations: SessionIterations
    slippage: SessionSlippage
    fixingbar: SessionFixingbar
    status: SessionStatus
    user: DomainUser = field_relationship(init=False)
    decisions: list[DomainDecision] = field_relationship(init=False)

    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> Self:
        raise NotImplementedError

    @classmethod
    def _select_random_ticker(cls, provider: Provider) -> Ticker:
        """Select one random ticker from the short list for current mode"""
        mode_random_tickers = cls.random_tickers.split(",")
        ticker_symbol = choice(mode_random_tickers)
        try:
            ticker = provider._get_ticker_by_symbol(ticker_symbol)
        except MemoryObjectNotFoundError as e:
            raise SessionConfigurationError from e
        return ticker

    def bound_to_user(self, user: DomainUser) -> Self:
        self.user = user
        return self


@define(kw_only=True, slots=False, hash=True)
class DomainSessionClassic(DomainSession):
    random_tickers = Settings().provider.RANDOM_TICKERS_STOCKS

    @classmethod
    def create(cls, provider: Provider) -> Self:
        session = cls(
            mode=SessionMode.classic,
            ticker=cls._select_random_ticker(provider),
            timeframe=SessionTimeframe.daily,
            barsnumber=SessionBarsnumber.bars70,
            timelimit=SessionTimelimit.seconds60,
            iterations=SessionIterations.iterations5,
            slippage=SessionSlippage.average,
            fixingbar=SessionFixingbar.bar20,
            status=SessionStatus.created,
        )
        return session


@define(kw_only=True, slots=False, hash=True)
class DomainSessionBlitz(DomainSession):
    random_tickers = Settings().provider.RANDOM_TICKERS_STOCKS

    @classmethod
    def create(cls, provider: Provider) -> Self:
        session = cls(
            mode=SessionMode.blitz,
            ticker=cls._select_random_ticker(provider),
            timeframe=SessionTimeframe.minutes5,
            barsnumber=SessionBarsnumber.bars30,
            timelimit=SessionTimelimit.seconds5,
            iterations=SessionIterations.iterations10,
            slippage=SessionSlippage.low,
            fixingbar=SessionFixingbar.bar10,
            status=SessionStatus.created,
        )
        return session


@define(kw_only=True, slots=False, hash=True)
class DomainSessionCrypto(DomainSession):
    random_tickers = Settings().provider.RANDOM_TICKERS_CRYPTO

    @classmethod
    def create(cls, provider: Provider) -> Self:
        session = cls(
            mode=SessionMode.crypto,
            ticker=cls._select_random_ticker(provider),
            timeframe=SessionTimeframe.daily,
            barsnumber=SessionBarsnumber.bars50,
            timelimit=SessionTimelimit.seconds30,
            iterations=SessionIterations.iterations10,
            slippage=SessionSlippage.low,
            fixingbar=SessionFixingbar.bar10,
            status=SessionStatus.created,
        )
        return session


@define(kw_only=True, slots=False, hash=True)
class DomainSessionCustom(DomainSession):
    @classmethod
    def create(
        cls,
        provider: Provider,
        ticker_symbol: str,
        timeframe: str,
        barsnumber: int,
        timelimit: int,
        iterations: int,
        slippage: Decimal,
        fixingbar: int,
    ) -> Self:
        session = cls(
            mode=SessionMode.custom,
            ticker=provider._get_ticker_by_symbol(ticker_symbol),
            timeframe=SessionTimeframe(timeframe),
            barsnumber=SessionBarsnumber(barsnumber),
            timelimit=SessionTimelimit(timelimit),
            iterations=SessionIterations(iterations),
            slippage=SessionSlippage(slippage),
            fixingbar=SessionFixingbar(fixingbar),
            status=SessionStatus.created,
        )
        return session


@define(kw_only=True, slots=False, hash=True)
class SessionOptions(metaclass=SingletonMeta):
    """Container with all possible parameters (options) of the Session"""

    all_ticker: list[Ticker]
    all_timeframe: tuple[SessionTimeframe, ...] = tuple(SessionTimeframe)
    all_barsnumber: tuple[SessionBarsnumber, ...] = tuple(SessionBarsnumber)
    all_timelimit: tuple[SessionTimelimit, ...] = tuple(SessionTimelimit)
    all_iterations: tuple[SessionIterations, ...] = tuple(SessionIterations)
    all_slippage: tuple[SessionSlippage, ...] = tuple(SessionSlippage)
    all_fixingbar: tuple[SessionFixingbar, ...] = tuple(SessionFixingbar)
