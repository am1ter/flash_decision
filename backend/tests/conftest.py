import csv
import uuid
from pathlib import Path
from typing import ClassVar

import pandas as pd
import pytest

from app.api.schemas.session import ReqSession
from app.api.schemas.user import ReqSignIn, ReqSignUp
from app.domain.session_provider import (
    ProviderAlphaVantageCrypto,
    ProviderAlphaVantageStocks,
    Ticker,
    csv_table,
)
from app.domain.user import DomainUser
from app.system.constants import (
    SessionBarsnumber,
    SessionFixingbar,
    SessionIterations,
    SessionMode,
    SessionSlippage,
    SessionTimeframe,
    SessionTimelimit,
    TickerType,
    UserStatus,
)


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
def mock_ticker() -> Ticker:
    return Ticker(ticker_type=TickerType.stock, exchange="Mock", symbol="MOCK", name="Mock ticker")


class ProviderAVStocksMockSuccess(ProviderAlphaVantageStocks):
    def _download_csv(self) -> csv_table:
        path = Path(__file__).parent / "mock_data" / "provider_av_stocks_mock_success_tickers.csv"
        with path.open() as file:
            csv_table = csv.reader(file.read().splitlines(), delimiter=",")
        next(csv_table)  # skip table header
        return list(csv_table)

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        path = Path(__file__).parent / "mock_data" / "provider_av_stocks_mock_success_data.json"
        mock_data_raw = pd.read_json(path)
        return pd.DataFrame.from_dict(mock_data_raw)


class ProviderAVCryptoMockSuccess(ProviderAlphaVantageCrypto):
    def _download_csv(self) -> csv_table:
        path = Path(__file__).parent / "mock_data" / "provider_av_crypto_mock_success_tickers.csv"
        with path.open() as file:
            csv_table = csv.reader(file.read().splitlines(), delimiter=",")
        next(csv_table)  # skip table header
        return list(csv_table)

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        path = Path(__file__).parent / "mock_data" / "provider_av_crypto_mock_success_data.json"
        mock_data_raw = pd.read_json(path)
        return pd.DataFrame.from_dict(mock_data_raw)


class ProviderAVStocksMockFailureBroken(ProviderAlphaVantageStocks):
    all_tickers: ClassVar[dict[str, Ticker]] = {}

    def _download_csv(self) -> csv_table:
        return [
            ["", "", "NASDAQ", "Stock", "13.03.1986", "null", "Active"],
            ["AAPL", "Apple Inc", "NASDAQ", "Stock", "12.12.1980", "null", "Active"],
        ]

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


class ProviderAVCryptoMockFailureBroken(ProviderAlphaVantageCrypto):
    all_tickers: ClassVar[dict[str, Ticker]] = {}

    def _download_csv(self) -> csv_table:
        return [["", "Bitcoin"], ["ETH", "Ethereum"]]

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


class ProviderAVStocksMockFailureBlank(ProviderAlphaVantageStocks):
    all_tickers: ClassVar[dict[str, Ticker]] = {}

    def _download_csv(self) -> csv_table:
        return []

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        mock_data_raw: dict[str, list] = {}
        return pd.DataFrame.from_dict(mock_data_raw)


class ProviderAVCryptoMockFailureBlank(ProviderAlphaVantageCrypto):
    all_tickers: ClassVar[dict[str, Ticker]] = {}

    def _download_csv(self) -> csv_table:
        return []

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        mock_data_raw: dict[str, list] = {}
        return pd.DataFrame.from_dict(mock_data_raw)


@pytest.fixture()
def req_session_params_custom() -> ReqSession:
    return ReqSession(
        mode=SessionMode.custom.value,
        ticker_type=TickerType.stock.value,
        ticker_symbol="AAPL",
        barsnumber=SessionBarsnumber.bars50.value,
        fixingbar=SessionFixingbar.bar20.value,
        iterations=SessionIterations.iterations10.value,
        slippage=SessionSlippage.low.value,
        timeframe=SessionTimeframe.minutes15.value,
        timelimit=SessionTimelimit.seconds60.value,
    )
