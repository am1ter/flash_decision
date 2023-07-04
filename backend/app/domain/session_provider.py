import csv
from typing import Protocol, TypeAlias

import pandas as pd
import requests
from alpha_vantage.async_support.cryptocurrencies import CryptoCurrencies
from alpha_vantage.async_support.timeseries import TimeSeries
from attrs import define, field, validators

from app.domain.base import ValueObjectJson
from app.system.config import settings
from app.system.constants import SessionTimeframe, TickerType
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
class Ticker(ValueObjectJson):
    ticker_type: TickerType = field(converter=TickerType)
    exchange: str
    symbol: str = field(validator=validators.min_len(1))
    name: str


class Provider(Protocol):
    """Protocol for setting up custom data providers"""

    all_tickers: dict[str, Ticker]

    def get_tickers(self) -> dict[str, Ticker]:
        ...

    async def get_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        ...


class ProviderAlphaVantage:
    """
    Data provider for USA stocks market and cryptocurrencies market.
    Documentation: https://www.alphavantage.co/documentation/
    """

    all_tickers: dict[str, Ticker] = {}
    url_root = "https://www.alphavantage.co"
    api_key = settings.ALPHAVANTAGE_API_KEY
    url_get_list: str
    data_cols_final = ["datetime", "open", "high", "low", "close", "volume"]

    def _download_csv(self) -> csv_table:
        r = requests.get(self.url_get_list)
        if r.status_code != 200:
            raise ProviderAccessError
        tickers_bytes = r.content.decode("utf-8")
        csv_table = csv.reader(tickers_bytes.splitlines(), delimiter=",")
        next(csv_table)  # skip table header
        return list(csv_table)

    def _process_csv(self, csv_table: csv_table) -> dict[str, Ticker]:
        raise NotImplementedError

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        raise NotImplementedError

    @classmethod
    def _transform_df_quotes(cls, df_quotes: pd.DataFrame) -> pd.DataFrame:
        # Validate df is not empty
        if df_quotes.empty:
            raise ProviderInvalidDataError

        # Use pyarrow engine to work with pandas
        df_quotes = pd.DataFrame.convert_dtypes(df_quotes, dtype_backend="pyarrow")

        # Drop extra columns
        cols_to_del = [col for col in df_quotes.columns if col not in cls.data_cols_final]
        df_quotes = df_quotes.drop(cols_to_del, axis=1)
        if list(df_quotes.columns) != cls.data_cols_final:
            raise ProviderInvalidDataError

        # Convert column from string to datetime
        df_quotes["datetime"] = pd.to_datetime(df_quotes["datetime"])

        return df_quotes

    def get_tickers(self, force: bool | None = None) -> dict[str, Ticker]:
        if not self.all_tickers or force:
            # Do not crash the app if the list of tickers is not available
            try:
                csv_table = self._download_csv()
                self.all_tickers = self._process_csv(csv_table)
            except (ProviderAccessError, ValueError):
                self.all_tickers = {}
            if not self.all_tickers:
                logger.exception(exc_info=ProviderAccessError)
        return self.all_tickers

    async def get_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        data = await self._download_data(ticker, timeframe)
        data = self._transform_df_quotes(data)
        return data


class ProviderAlphaVantageStocks(ProviderAlphaVantage):
    data_cols_intraday = {
        "index": "datetime",
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close",
        "5. volume": "volume",
    }
    data_cols_daily = {
        "index": "datetime",
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close",
        "6. volume": "volume",
    }

    def __init__(self) -> None:
        self.url_get_list = f"{self.url_root}/query?function=LISTING_STATUS&apikey={self.api_key}"
        self.exporter = TimeSeries(
            key=settings.ALPHAVANTAGE_API_KEY, output_format="pandas", indexing_type="integer"
        )

    def _process_csv(self, csv_table: csv_table) -> dict[str, Ticker]:
        all_tickers = {}
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
                all_tickers[ticker.symbol] = ticker
        return all_tickers

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        """Send request, use data with quotes, ignore metadata (_), rename columns"""
        match timeframe:
            case SessionTimeframe.daily:
                data, _ = await self.exporter.get_daily_adjusted(ticker.symbol, outputsize="full")
                data = data.rename(self.data_cols_daily, axis="columns")
            case _:
                data, _ = await self.exporter.get_intraday(
                    ticker.symbol, interval=timeframe.value, outputsize="full"
                )
                data = data.rename(self.data_cols_intraday, axis="columns")
        return data


class ProviderAlphaVantageCrypto(ProviderAlphaVantage):
    related_columns_daily = {
        "index": "datetime",
        "1a. open (USD)": "open",
        "2b. high (USD)": "high",
        "3b. low (USD)": "low",
        "4b. close (USD)": "close",
        "5. volume": "volume",
    }

    def __init__(self) -> None:
        self.url_get_list = f"{self.url_root}/digital_currency_list/"
        self.exporter = CryptoCurrencies(
            key=settings.ALPHAVANTAGE_API_KEY, output_format="pandas", indexing_type="integer"
        )

    def _process_csv(self, csv_table: csv_table) -> dict[str, Ticker]:
        all_tickers = {}
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
                all_tickers[ticker.symbol] = ticker
        return all_tickers

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        """Send request, use data with quotes, ignore metadata (_), rename columns"""
        match timeframe:
            case SessionTimeframe.daily:
                data, _ = await self.exporter.get_digital_currency_daily(
                    ticker.symbol, market=settings.CRYPTO_PRICE_CURRENCY
                )
                data = data.rename(self.related_columns_daily, axis="columns")
            case _:
                raise UnsupportedModeError
        return data
