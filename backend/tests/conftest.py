import uuid

import pandas as pd
import pytest

from app.api.schemas.user import ReqSignIn, ReqSignUp
from app.domain.session_provider import (
    ProviderAlphaVantageCrypto,
    ProviderAlphaVantageStocks,
    Ticker,
    csv_table,
)
from app.domain.user import DomainUser
from app.system.constants import TickerType, Timeframe, UserStatus


@pytest.fixture()
def user_domain() -> DomainUser:
    return DomainUser(
        email=f"test-user-{uuid.uuid4()}@alekseisemenov.ru",
        name="test-user",
        password=str(uuid.uuid4()),
        status=UserStatus.active,
    )


@pytest.fixture(scope="module")
def req_sign_up() -> ReqSignUp:
    return ReqSignUp(
        email=f"test-user-{uuid.uuid4()}@alekseisemenov.ru",
        name="test-user",
        password=str(uuid.uuid4()),
    )


@pytest.fixture(scope="module")
def req_sign_in(req_sign_up: ReqSignUp) -> ReqSignIn:
    return ReqSignIn(username=req_sign_up.email, password=req_sign_up.password)


@pytest.fixture()
def ticker() -> Ticker:
    return Ticker(ticker_type=TickerType.stock, exchange="Mock", symbol="MOCK", name="Mock ticker")


class ProviderAVStocksMockSuccess(ProviderAlphaVantageStocks):
    def _download_csv(self) -> csv_table:
        return [
            ["MSFT", "Microsoft Corp", "NASDAQ", "Stock", "13.03.1986", "null", "Active"],
            ["AAPL", "Apple Inc", "NASDAQ", "Stock", "12.12.1980", "null", "Active"],
            ["BA", "Boeing Company", "NYSE", "Stock", "02.01.1962", "null", "Active"],
        ]

    async def _download_data(self, ticker: Ticker, timeframe: Timeframe) -> pd.DataFrame:
        mock_data_raw = {
            "datetime": ["2023-06-28", "2023-06-27"],
            "open": [100.00, 101.05],
            "high": [105.00, 106.05],
            "low": [95.50, 96.60],
            "close": [101.05, 102.10],
            "volume": [2000, 2020],
        }
        return pd.DataFrame.from_dict(mock_data_raw)


class ProviderAVCryptoMockSuccess(ProviderAlphaVantageCrypto):
    def _download_csv(self) -> csv_table:
        return [["BTC", "Bitcoin"], ["ETH", "Ethereum"]]

    async def _download_data(self, ticker: Ticker, timeframe: Timeframe) -> pd.DataFrame:
        mock_data_raw = {
            "datetime": ["2010-06-28 10:00", "2010-06-28 10:05"],
            "open": [100.00, 101.05],
            "high": [105.00, 106.05],
            "low": [95.50, 96.60],
            "close": [101.05, 102.10],
            "volume": [2000, 2020],
        }
        return pd.DataFrame.from_dict(mock_data_raw)


class ProviderAVStocksMockFailureBroken(ProviderAlphaVantageStocks):
    def _download_csv(self) -> csv_table:
        return [
            ["", "", "NASDAQ", "Stock", "13.03.1986", "null", "Active"],
            ["AAPL", "Apple Inc", "NASDAQ", "Stock", "12.12.1980", "null", "Active"],
        ]

    async def _download_data(self, ticker: Ticker, timeframe: Timeframe) -> pd.DataFrame:
        mock_data_raw = {
            "datetime": ["2010-06-28 10:00", "2010-06-28 10:05"],
            "wrong_col_name": [100.00, 101.05],
            "high": [105.00, 106.05],
            "low": [95.50, 96.60],
            "close": [101.05, 102.10],
            "volume": [2000, 2020],
        }
        return pd.DataFrame.from_dict(mock_data_raw)


class ProviderAVCryptoMockFailureBroken(ProviderAlphaVantageCrypto):
    def _download_csv(self) -> csv_table:
        return [["", "Bitcoin"], ["ETH", "Ethereum"]]

    async def _download_data(self, ticker: Ticker, timeframe: Timeframe) -> pd.DataFrame:
        mock_data_raw = {
            "datetime": ["2010-06-28 10:00", "2010-06-28 10:05"],
            "wrong_col_name": [100.00, 101.05],
            "high": [105.00, 106.05],
            "low": [95.50, 96.60],
            "close": [101.05, 102.10],
            "volume": [2000, 2020],
        }
        return pd.DataFrame.from_dict(mock_data_raw)


class ProviderAVStocksMockFailureBlank(ProviderAlphaVantageStocks):
    def _download_csv(self) -> csv_table:
        return []

    async def _download_data(self, ticker: Ticker, timeframe: Timeframe) -> pd.DataFrame:
        mock_data_raw: dict[str, list] = {}
        return pd.DataFrame.from_dict(mock_data_raw)


class ProviderAlVCryptoMockFailureBlank(ProviderAlphaVantageCrypto):
    def _download_csv(self) -> csv_table:
        return []

    async def _download_data(self, ticker: Ticker, timeframe: Timeframe) -> pd.DataFrame:
        mock_data_raw: dict[str, list] = {}
        return pd.DataFrame.from_dict(mock_data_raw)
