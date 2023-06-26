import csv
from typing import Protocol, TypeAlias

import pandas as pd
import requests
from alpha_vantage.async_support.cryptocurrencies import CryptoCurrencies
from alpha_vantage.async_support.timeseries import TimeSeries
from attrs import define, field, validators

from app.system.config import settings
from app.system.constants import TickerType, Timeframe
from app.system.exceptions import (
    ProviderAccessError,
    ProviderInvalidDataError,
    UnsupportedModeError,
)
from app.system.logger import create_logger

# Create logger
logger = create_logger("backend.domain.session_provider")

csv_table: TypeAlias = list[list[str]]


@define
class Ticker:
    ticker_type: TickerType
    exchange: str
    symbol: str = field(validator=validators.min_len(1))
    name: str


class Provider(Protocol):
    """Protocol for setting up custom data providers"""

    all_tickers: list[Ticker]

    def get_list(self) -> list[Ticker]:
        ...

    async def get_data(self, ticker: Ticker, timeframe: Timeframe) -> pd.DataFrame:
        ...


class ProviderAlphaVantage:
    """
    Data provider for USA stocks market and cryptocurrencies market.
    Documentation: https://www.alphavantage.co/documentation/
    """

    all_tickers: list[Ticker] = []
    url_root = "https://www.alphavantage.co"
    api_key = settings.ALPHAVANTAGE_API_KEY
    url_get_list: str

    def _download_csv(self) -> csv_table:
        r = requests.get(self.url_get_list)
        if r.status_code != 200:
            raise ProviderAccessError
        tickers_bytes = r.content.decode("utf-8")
        csv_table = csv.reader(tickers_bytes.splitlines(), delimiter=",")
        next(csv_table)  # skip table header
        return list(csv_table)

    def _process_csv(self, csv_table: csv_table) -> list[Ticker]:
        raise NotImplementedError

    async def _download_data(self, ticker: Ticker, timeframe: Timeframe) -> pd.DataFrame:
        raise NotImplementedError

    def get_list(self, force: bool | None = None) -> list[Ticker]:
        if not self.all_tickers or force:
            # Do not crash the app if the list of tickers is not available
            try:
                csv_table = self._download_csv()
                self.all_tickers = self._process_csv(csv_table)
            except (ProviderAccessError, ValueError):
                self.all_tickers = []
            if not self.all_tickers:
                logger.exception(exc_info=ProviderAccessError)
        return self.all_tickers

    async def get_data(self, ticker: Ticker, timeframe: Timeframe) -> pd.DataFrame:
        data = await self._download_data(ticker, timeframe)
        if data.empty:
            raise ProviderInvalidDataError
        return data


class ProviderAlphaVantageStocks(ProviderAlphaVantage):
    def __init__(self) -> None:
        self.url_get_list = f"{self.url_root}/query?function=LISTING_STATUS&apikey={self.api_key}"
        self.exporter = TimeSeries(key=settings.ALPHAVANTAGE_API_KEY, output_format="pandas")

    def _process_csv(self, csv_table: csv_table) -> list[Ticker]:
        all_tickers = []
        for symbol, name, exchange, ticker_type, *_ in csv_table:
            # Do not crash the app if the there is broken tickers in the csv
            try:
                ticker = Ticker(
                    ticker_type=TickerType(ticker_type),
                    exchange=exchange,
                    symbol=symbol,
                    name=name,
                )
            except ValueError:
                logger.error(  # noqa: TRY400
                    event=ProviderInvalidDataError.msg,
                    cls=self.__class__.__name__,
                    function="_process_csv",
                    record=(symbol, name, exchange, ticker_type),
                )
            else:
                all_tickers.append(ticker)
        return all_tickers

    async def _download_data(self, ticker: Ticker, timeframe: Timeframe) -> pd.DataFrame:
        """Send request, use data with quotes, ignore metadata (_)"""
        match timeframe:
            case Timeframe.daily:
                data, _ = await self.exporter.get_daily_adjusted(ticker.symbol)
            case _:
                data, _ = await self.exporter.get_intraday(ticker.symbol, interval=timeframe.value)
        return data


class ProviderAlphaVantageCrypto(ProviderAlphaVantage):
    def __init__(self) -> None:
        self.url_get_list = f"{self.url_root}/digital_currency_list/"
        self.exporter = CryptoCurrencies(key=settings.ALPHAVANTAGE_API_KEY, output_format="pandas")

    def _process_csv(self, csv_table: csv_table) -> list[Ticker]:
        all_tickers = []
        for currency_code, currency_name in csv_table:
            try:
                ticker = Ticker(
                    ticker_type=TickerType("Crypto"),
                    exchange=settings.CRYPTO_PRICE_CURRENCY,
                    symbol=currency_code,
                    name=currency_name,
                )
            except ValueError:
                logger.error(  # noqa: TRY400
                    event=ProviderInvalidDataError.msg,
                    cls=self.__class__.__name__,
                    function="_process_csv",
                    record=(currency_code, currency_name),
                )
            else:
                all_tickers.append(ticker)
        return all_tickers

    async def _download_data(self, ticker: Ticker, timeframe: Timeframe) -> pd.DataFrame:
        """Send request, use data with quotes, ignore metadata (_)"""
        match timeframe:
            case Timeframe.daily:
                data, _ = await self.exporter.get_digital_currency_daily(
                    ticker.symbol, market=settings.CRYPTO_PRICE_CURRENCY
                )
            case _:
                raise UnsupportedModeError
        return data
