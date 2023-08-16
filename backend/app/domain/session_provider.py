import contextlib
from abc import ABCMeta, abstractmethod
from typing import ClassVar, TypeAlias, cast

import pandas as pd
import structlog
from attrs import define, field, validators

from app.domain.base import ValueObjectJson
from app.domain.cache import Cache
from app.system.constants import SessionTimeframe, TickerType
from app.system.exceptions import (
    CacheConnectionError,
    CacheObjectNotFoundError,
    MemoryObjectNotFoundError,
    ProviderAccessError,
)

# Create logger
logger = structlog.get_logger()


@define
class Ticker(ValueObjectJson):
    ticker_type: TickerType = field(converter=TickerType)
    exchange: str
    symbol: str = field(validator=validators.min_len(1))
    name: str


csv_table: TypeAlias = list[list[str]]
tickers: TypeAlias = dict[str, Ticker]


@define(kw_only=False, slots=False, hash=True)
class TickerCol(metaclass=ABCMeta):
    """Part of the `Provider`. Contains logic related to `Ticker` downloading and processing"""

    _tickers: ClassVar[tickers] = {}
    cache: Cache

    @abstractmethod
    async def _download_raw_tickers(self) -> csv_table:
        raise NotImplementedError

    @abstractmethod
    def _process_tickers(self, raw_tickers: csv_table) -> tickers:
        raise NotImplementedError

    @property
    def _cache_key(self) -> str:
        return f"{self.__class__.__name__}:_tickers"

    @classmethod
    def _get_processed_tickers_from_memory(cls) -> tickers:
        if not cls._tickers:
            raise MemoryObjectNotFoundError
        return cls._tickers

    async def _get_raw_tickers_from_cache(self) -> csv_table:
        if not self.cache:
            raise CacheObjectNotFoundError
        raw_tickers = cast(csv_table, await self.cache.get(self._cache_key))
        return raw_tickers

    async def _get_raw_tickers_from_provider(self) -> csv_table:
        tickers_col_raw = await self._download_raw_tickers()
        if self.cache:
            with contextlib.suppress(CacheConnectionError):
                await self.cache.set(self._cache_key, tickers_col_raw)
        return tickers_col_raw

    async def load_processed_tickers(self) -> tickers:
        """Key method in the class. Represents an ETL pipeline."""
        with contextlib.suppress(MemoryObjectNotFoundError):
            return self._get_processed_tickers_from_memory()

        try:
            tickers_col_raw = await self._get_raw_tickers_from_cache()
        except (CacheObjectNotFoundError, CacheConnectionError):
            tickers_col_raw = await self._get_raw_tickers_from_provider()

        return self._process_tickers(tickers_col_raw)


class DataExporter(metaclass=ABCMeta):
    """Part of the `Provider`. Contains logic related to downloading and processing quotes"""

    @abstractmethod
    async def get_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        raise NotImplementedError


@define(kw_only=False, slots=False, hash=True)
class Provider(metaclass=ABCMeta):
    """
    Abstract class for setting up custom data providers.
    Here used Composition principle for the class decomposition.
    """

    ticker_col: TickerCol
    data_exporter: DataExporter

    @abstractmethod
    async def healthcheck(self) -> bool:
        raise NotImplementedError

    def is_tickers_loaded(self) -> bool:
        return bool(self.ticker_col._tickers)

    async def get_tickers(self) -> tickers:
        return await self.ticker_col.load_processed_tickers()

    def get_ticker_by_symbol(self, symbol: str) -> Ticker:
        try:
            return self.ticker_col._tickers[symbol]
        except KeyError as e:
            if not self.ticker_col._tickers:
                raise ProviderAccessError from e
            raise MemoryObjectNotFoundError from e

    async def get_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        return await self.data_exporter.get_data(ticker, timeframe)
