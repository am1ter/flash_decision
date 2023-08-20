import csv
from pathlib import Path
from typing import ClassVar

import pandas as pd
from attrs import define

from app.domain.interfaces.cache import Cache
from app.domain.interfaces.provider import csv_table
from app.domain.ticker import Ticker, tickers
from app.infrastructure.external_api.provider import (
    DataExporterAlphaVantage,
    ProviderAlphaVantageCrypto,
    ProviderAlphaVantageStocks,
    TickerColAlphaVantageCrypto,
    TickerColAlphaVantageStocks,
)
from app.system.constants import SessionTimeframe
from tests.conftest import df_quotes_crypto, df_quotes_stocks


class TickerColStocksMockSuccess(TickerColAlphaVantageStocks):
    _tickers: ClassVar[tickers] = {}

    async def _download_raw_tickers(self) -> csv_table:
        root = Path(__file__).parent.parent
        path = root / "_mock_data" / "provider_av_stocks_mock_success_tickers.csv"
        with path.open() as file:
            csv_table = csv.reader(file.read().splitlines(), delimiter=",")
        next(csv_table)  # skip table header
        return list(csv_table)


class TickerColCryptoMockSuccess(TickerColAlphaVantageCrypto):
    _tickers: ClassVar[tickers] = {}

    async def _download_raw_tickers(self) -> csv_table:
        root = Path(__file__).parent.parent
        path = root / "_mock_data" / "provider_av_crypto_mock_success_tickers.csv"
        with path.open() as file:
            csv_table = csv.reader(file.read().splitlines(), delimiter=",")
        next(csv_table)  # skip table header
        return list(csv_table)


class TickerColStocksMockBroken(TickerColAlphaVantageStocks):
    _tickers: ClassVar[tickers] = {}

    async def _download_raw_tickers(self) -> csv_table:
        return [
            ["", "", "NASDAQ", "Stock", "13.03.1986", "null", "Active"],
            ["AAPL", "Apple Inc", "NASDAQ", "Stock", "12.12.1980", "null", "Active"],
        ]


class TickerColCryptoMockBroken(TickerColAlphaVantageCrypto):
    _tickers: ClassVar[tickers] = {}

    async def _download_raw_tickers(self) -> csv_table:
        return [["", "Bitcoin"], ["ETH", "Ethereum"]]


class TickerColStocksMockBlank(TickerColAlphaVantageStocks):
    _tickers: ClassVar[tickers] = {}

    async def _download_raw_tickers(self) -> csv_table:
        return []


class TickerColCryptoMockBlank(TickerColAlphaVantageCrypto):
    _tickers: ClassVar[tickers] = {}

    async def _download_raw_tickers(self) -> csv_table:
        return []


class DataExporterStocksMockSuccess(DataExporterAlphaVantage):
    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        return df_quotes_stocks()


class DataExporterCryptoMockSuccess(DataExporterAlphaVantage):
    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        return df_quotes_crypto()


class DataExporterStocksMockBroken(DataExporterAlphaVantage):
    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        mock_data_raw = {
            "datetime": ["2010-06-28 10:00", "2010-06-28 10:05"],
            "wrong_col_name": [100.00, 101.05],
            "high": [105.00, 106.05],
            "low": [95.50, 96.60],
            "close": [101.05, 102.10],
            "volume": [2000, 2020],
        }
        return pd.DataFrame.from_dict(mock_data_raw)


class DataExporterCryptoMockBroken(DataExporterAlphaVantage):
    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        mock_data_raw = {
            "datetime": ["2010-06-28 10:00", "2010-06-28 10:05"],
            "wrong_col_name": [100.00, 101.05],
            "high": [105.00, 106.05],
            "low": [95.50, 96.60],
            "close": [101.05, 102.10],
            "volume": [2000, 2020],
        }
        return pd.DataFrame.from_dict(mock_data_raw)


class DataExporterStocksMockBlank(DataExporterAlphaVantage):
    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        mock_data_raw: dict[str, list] = {}
        return pd.DataFrame.from_dict(mock_data_raw)


class DataExporterCryptoMockBlank(DataExporterAlphaVantage):
    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        mock_data_raw: dict[str, list] = {}
        return pd.DataFrame.from_dict(mock_data_raw)


@define(kw_only=False, slots=False, hash=True)
class ProviderAVStocksMockSuccess(ProviderAlphaVantageStocks):
    cache: Cache = None  # type: ignore[assignment]
    ticker_col: TickerColStocksMockSuccess = TickerColStocksMockSuccess(cache)
    data_exporter: DataExporterStocksMockSuccess = DataExporterStocksMockSuccess()  # type: ignore[assignment]

    async def healthcheck(self) -> bool:
        return True


@define(kw_only=False, slots=False, hash=True)
class ProviderAVCryptoMockSuccess(ProviderAlphaVantageCrypto):
    cache: Cache = None  # type: ignore[assignment]
    ticker_col: TickerColCryptoMockSuccess = TickerColCryptoMockSuccess(cache)
    data_exporter: DataExporterCryptoMockSuccess = DataExporterCryptoMockSuccess()  # type: ignore[assignment]

    async def healthcheck(self) -> bool:
        return True


@define(kw_only=False, slots=False, hash=True)
class ProviderAVStocksMockBroken(ProviderAlphaVantageStocks):
    cache: Cache = None  # type: ignore[assignment]
    ticker_col: TickerColStocksMockBroken = TickerColStocksMockBroken(cache)
    data_exporter: DataExporterStocksMockBroken = DataExporterStocksMockBroken()  # type: ignore[assignment]


@define(kw_only=False, slots=False, hash=True)
class ProviderAVCryptoMockBroken(ProviderAlphaVantageCrypto):
    cache: Cache = None  # type: ignore[assignment]
    ticker_col: TickerColCryptoMockBroken = TickerColCryptoMockBroken(cache)
    data_exporter: DataExporterCryptoMockBroken = DataExporterCryptoMockBroken()  # type: ignore[assignment]


@define(kw_only=False, slots=False, hash=True)
class ProviderAVStocksMockBlank(ProviderAlphaVantageStocks):
    cache: Cache = None  # type: ignore[assignment]
    ticker_col: TickerColStocksMockBlank = TickerColStocksMockBlank(cache)
    data_exporter: DataExporterStocksMockBlank = DataExporterStocksMockBlank()  # type: ignore[assignment]


@define(kw_only=False, slots=False, hash=True)
class ProviderAVCryptoMockBlank(ProviderAlphaVantageCrypto):
    cache: Cache = None  # type: ignore[assignment]
    ticker_col: TickerColCryptoMockBlank = TickerColCryptoMockBlank(cache)
    data_exporter: DataExporterCryptoMockBlank = DataExporterCryptoMockBlank()  # type: ignore[assignment]


provider_av_stocks_mock_success = ProviderAVStocksMockSuccess()
provider_av_crypto_mock_success = ProviderAVCryptoMockSuccess()
provider_av_stocks_mock_broken = ProviderAVStocksMockBroken()
provider_av_crypto_mock_broken = ProviderAVCryptoMockBroken()
provider_av_stocks_mock_blank = ProviderAVStocksMockBlank()
provider_av_crypto_mock_blank = ProviderAVCryptoMockBlank()
