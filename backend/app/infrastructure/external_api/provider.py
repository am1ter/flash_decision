import csv
from abc import ABCMeta, abstractmethod
from typing import ClassVar

import httpx
import pandas as pd
import structlog
from alpha_vantage.async_support.cryptocurrencies import CryptoCurrencies
from alpha_vantage.async_support.timeseries import TimeSeries
from attrs import define, field

from app.domain.interfaces.cache import Cache
from app.domain.interfaces.provider import DataExporter, Provider, TickerCol, csv_table
from app.domain.ticker import Ticker, tickers
from app.system.config import Settings
from app.system.constants import SessionTimeframe, TickerType
from app.system.exceptions import (
    ProviderAccessError,
    ProviderInvalidDataError,
    ProviderRateLimitExceededError,
    UnsupportedModeError,
)

# Create logger
logger = structlog.get_logger()

url_root = "https://www.alphavantage.co"
api_key_stocks = Settings().provider.ALPHAVANTAGE_API_KEY_STOCKS
api_key_crypto = Settings().provider.ALPHAVANTAGE_API_KEY_CRYPTO


@define(kw_only=False, slots=False, hash=True)
class TickerColAlphaVantage(TickerCol, metaclass=ABCMeta):
    url_get_all: ClassVar[str]

    @abstractmethod
    def _process_csv(self, csv_table: csv_table) -> tickers:
        raise NotImplementedError

    async def _download_raw_tickers(self) -> csv_table:
        async with httpx.AsyncClient() as client:
            r = await client.get(self.url_get_all)
        if r.status_code != 200:
            raise ProviderAccessError
        tickers_bytes = r.content.decode("utf-8")
        csv_table = csv.reader(tickers_bytes.splitlines(), delimiter=",")
        next(csv_table)  # skip table header
        raw_tickers = list(csv_table)
        if not raw_tickers:
            raise ProviderAccessError
        return raw_tickers

    def _process_tickers(self, raw_tickers: csv_table) -> tickers:
        if not self._tickers:
            # Do not crash the app if the list of tickers is not available
            try:
                self.__class__._tickers = self._process_csv(raw_tickers)
            except (ProviderAccessError, ValueError):
                self.__class__._tickers = {}
            if not self._tickers:
                logger.error_finish(
                    cls=self.__class__, show_func_name=True, error=ProviderAccessError.msg
                )
        return self._tickers


@define(kw_only=False, slots=False, hash=True)
class TickerColAlphaVantageStocks(TickerColAlphaVantage):
    url_get_all: ClassVar[str] = f"{url_root}/query?function=LISTING_STATUS&apikey={api_key_stocks}"

    def _process_csv(self, csv_table: csv_table) -> tickers:
        tickers = {}
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
                logger.error_finish(
                    cls=self.__class__,
                    show_func_name=True,
                    error=ProviderInvalidDataError.msg,
                    record=(symbol, name, exchange, ticker_type),
                )
            else:
                tickers[ticker.symbol] = ticker
        return tickers


@define(kw_only=False, slots=False, hash=True)
class TickerColAlphaVantageCrypto(TickerColAlphaVantage):
    url_get_all: ClassVar[str] = f"{url_root}/digital_currency_list/"

    def _process_csv(self, csv_table: csv_table) -> tickers:
        _tickers = {}
        for currency_code, currency_name in csv_table:
            try:
                ticker = Ticker(
                    ticker_type=TickerType("Crypto"),
                    exchange=Settings().provider.CRYPTO_PRICE_CURRENCY,
                    symbol=currency_code,
                    name=currency_name,
                )
            except ValueError:
                logger.error_finish(
                    cls=self.__class__,
                    show_func_name=True,
                    error=ProviderInvalidDataError.msg,
                    record=(currency_code, currency_name),
                )
            else:
                _tickers[ticker.symbol] = ticker
        return _tickers


@define(kw_only=False, slots=False, hash=True)
class DataExporterAlphaVantage(DataExporter, metaclass=ABCMeta):
    data_cols_final: ClassVar[tuple[str, ...]] = ("datetime", "open", "high", "low", "close")

    @abstractmethod
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
        if list(df_quotes.columns) != list(cls.data_cols_final):
            raise ProviderInvalidDataError

        # Convert column from string to datetime
        df_quotes["datetime"] = pd.to_datetime(df_quotes["datetime"])

        return df_quotes

    async def get_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        data = await self._download_data(ticker, timeframe)
        data = self._transform_df_quotes(data)
        return data


@define(kw_only=False, slots=False, hash=True)
class DataExporterAlphaVantageStocks(DataExporterAlphaVantage):
    exporter: TimeSeries = field()

    @exporter.default
    def exporter_default(self) -> TimeSeries:
        return TimeSeries(key=api_key_stocks, output_format="pandas", indexing_type="integer")

    async def _download_data_intraday(
        self, ticker: Ticker, timeframe: SessionTimeframe
    ) -> pd.DataFrame:
        try:
            data, _ = await self.exporter.get_intraday(
                ticker.symbol, interval=timeframe.value, outputsize="full"
            )
        except ValueError as e:
            raise ProviderRateLimitExceededError from e
        data_cols_rename_map = {
            "index": "datetime",
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
        }
        data = data.rename(data_cols_rename_map, axis="columns")
        return data

    async def _download_data_daily(self, ticker: Ticker) -> pd.DataFrame:
        try:
            data, _ = await self.exporter.get_daily(ticker.symbol, outputsize="full")
        except ValueError as e:
            raise ProviderRateLimitExceededError from e
        data_cols_rename_map = {
            "index": "datetime",
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
        }
        data = data.rename(data_cols_rename_map, axis="columns")
        return data

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        """Send request, use data with quotes, ignore metadata (_), rename columns"""
        match timeframe:
            case SessionTimeframe.daily:
                data = await self._download_data_daily(ticker)
            case _:
                data = await self._download_data_intraday(ticker, timeframe)
        return data


@define(kw_only=False, slots=False, hash=True)
class DataExporterAlphaVantageCrypto(DataExporterAlphaVantage):
    exporter: CryptoCurrencies = field()

    @exporter.default
    def exporter_default(self) -> TimeSeries:
        return CryptoCurrencies(key=api_key_crypto, output_format="pandas", indexing_type="integer")

    async def _download_data_daily(self, ticker: Ticker) -> pd.DataFrame:
        try:
            data, _ = await self.exporter.get_digital_currency_daily(
                ticker.symbol, market=Settings().provider.CRYPTO_PRICE_CURRENCY
            )
        except ValueError as e:
            if "5 calls per minute" in e.args[0] or "limit for your free API key" in e.args[0]:
                raise ProviderRateLimitExceededError from e
            raise
        data_cols_rename_map = {
            "index": "datetime",
            "1b. open (USD)": "open",
            "2b. high (USD)": "high",
            "3b. low (USD)": "low",
            "4b. close (USD)": "close",
        }
        data = data.rename(data_cols_rename_map, axis="columns")
        return data

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        """Send request, use data with quotes, ignore metadata (_), rename columns"""
        match timeframe:
            case SessionTimeframe.daily:
                data = await self._download_data_daily(ticker)
            case _:
                raise UnsupportedModeError
        return data


@define(kw_only=False, slots=False, hash=True)
class ProviderAlphaVantage(Provider, metaclass=ABCMeta):
    """
    Data provider for USA stocks market and cryptocurrencies market.
    Documentation: https://www.alphavantage.co/documentation/
    """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    async def healthcheck(self) -> bool:
        api_key = "demo"
        url_healthcheck = f"{url_root}/query?function=MARKET_STATUS&apikey={api_key}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url_healthcheck)
        result = bool(r.status_code == 200)
        return result


@define(kw_only=False, slots=False, hash=True)
class ProviderAlphaVantageStocks(ProviderAlphaVantage):
    cache: Cache
    ticker_col: TickerColAlphaVantageStocks = field()
    data_exporter: DataExporterAlphaVantageStocks = field()

    @ticker_col.default
    def ticker_col_default(self) -> TimeSeries:
        return TickerColAlphaVantageStocks(self.cache)

    @data_exporter.default
    def data_exporter_default(self) -> TimeSeries:
        return DataExporterAlphaVantageStocks()


@define(kw_only=False, slots=False, hash=True)
class ProviderAlphaVantageCrypto(ProviderAlphaVantage):
    cache: Cache
    ticker_col: TickerColAlphaVantageCrypto = field()
    data_exporter: DataExporterAlphaVantageCrypto = field()

    @ticker_col.default
    def ticker_col_default(self) -> TimeSeries:
        return TickerColAlphaVantageCrypto(self.cache)

    @data_exporter.default
    def data_exporter_default(self) -> TimeSeries:
        return DataExporterAlphaVantageCrypto()
