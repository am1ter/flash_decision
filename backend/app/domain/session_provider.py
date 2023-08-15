from abc import ABCMeta, abstractmethod
from typing import ClassVar, TypeAlias

import pandas as pd
import structlog
from attrs import define, field, validators

from app.domain.base import ValueObjectJson
from app.system.constants import SessionTimeframe, TickerType
from app.system.exceptions import MemoryObjectNotFoundError, ProviderAccessError

# Create logger
logger = structlog.get_logger()

csv_table: TypeAlias = list[list[str]]


@define
class Ticker(ValueObjectJson):
    ticker_type: TickerType = field(converter=TickerType)
    exchange: str
    symbol: str = field(validator=validators.min_len(1))
    name: str


class Provider(metaclass=ABCMeta):
    """Protocol for setting up custom data providers"""

    _tickers: ClassVar[dict[str, Ticker]]

    @classmethod
    def _get_ticker_by_symbol(cls, symbol: str) -> Ticker:
        try:
            return cls._tickers[symbol]
        except KeyError as e:
            if not cls._tickers:
                raise ProviderAccessError from e
            raise MemoryObjectNotFoundError from e

    @classmethod
    def get_tickers(cls) -> dict[str, Ticker]:
        if not cls._tickers:
            raise MemoryObjectNotFoundError
        return cls._tickers

    @abstractmethod
    async def download_raw_tickers(self) -> csv_table:
        ...

    @abstractmethod
    def process_tickers(self, raw_tickers: csv_table) -> dict[str, Ticker]:
        ...

    @abstractmethod
    async def get_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        ...

    @abstractmethod
    async def healthcheck(self) -> bool:
        ...
