import csv
from pathlib import Path
from typing import ClassVar

import pandas as pd
import pytest
from uuid6 import uuid6

from app.api.schemas.session import ReqSession
from app.api.schemas.user import ReqSignIn, ReqSignUp
from app.domain.iteration import DomainIteration
from app.domain.session import DomainSession, DomainSessionCustom, SessionQuotes
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
    SessionStatus,
    SessionTimeframe,
    SessionTimelimit,
    TickerType,
    UserStatus,
)


@pytest.fixture()
def user_domain() -> DomainUser:
    return DomainUser(
        email=f"test-user-{uuid6()!s}@alekseisemenov.ru",
        name="test-user",
        password=str(uuid6()),
        status=UserStatus.active,
    )


def df_quotes_stocks() -> pd.DataFrame:
    path = Path(__file__).parent / "_mock_data" / "provider_av_stocks_mock_success_data.json"
    return pd.read_json(path)


def df_quotes_crypto() -> pd.DataFrame:
    path = Path(__file__).parent / "_mock_data" / "provider_av_crypto_mock_success_data.json"
    return pd.read_json(path)


@pytest.fixture()
def session(mock_ticker: Ticker, user_domain: DomainUser) -> DomainSession:
    session = DomainSessionCustom(
        mode=SessionMode.custom,
        ticker=mock_ticker,
        timeframe=SessionTimeframe.daily,
        barsnumber=SessionBarsnumber.bars70,
        timelimit=SessionTimelimit.seconds60,
        iterations=SessionIterations.iterations5,
        slippage=SessionSlippage.average,
        fixingbar=SessionFixingbar.bar20,
        status=SessionStatus.created,
    )
    session.user = user_domain
    return session


@pytest.fixture()
def session_quotes(session: DomainSession) -> SessionQuotes:
    return SessionQuotes.create(session=session, df_quotes=df_quotes_stocks())


@pytest.fixture()
def iteration(session_quotes: SessionQuotes) -> DomainIteration:
    data_path = Path(__file__).parent / "_mock_data" / "mock_iteration_01.json"
    df_quotes_iteration = pd.read_json(data_path)
    return DomainIteration(
        session_id=session_quotes.session._id,
        iteration_num=0,
        df_quotes=df_quotes_iteration,
        session=session_quotes.session,
    )


@pytest.fixture(scope="module")
def req_sign_up() -> ReqSignUp:
    return ReqSignUp(
        email=f"test-user-{uuid6()}@alekseisemenov.ru",
        name="test-user",
        password=str(uuid6()),
    )


@pytest.fixture(scope="module")
def req_sign_in(req_sign_up: ReqSignUp) -> ReqSignIn:
    return ReqSignIn(username=req_sign_up.email, password=req_sign_up.password)


@pytest.fixture()
def mock_ticker() -> Ticker:
    return Ticker(ticker_type=TickerType.stock, exchange="Mock", symbol="MOCK", name="Mock ticker")


class ProviderAVStocksMockSuccess(ProviderAlphaVantageStocks):
    async def download_raw_tickers(self) -> csv_table:
        path = Path(__file__).parent / "_mock_data" / "provider_av_stocks_mock_success_tickers.csv"
        with path.open() as file:
            csv_table = csv.reader(file.read().splitlines(), delimiter=",")
        next(csv_table)  # skip table header
        return list(csv_table)

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        return df_quotes_stocks()

    async def healthcheck(self) -> bool:
        return True


class ProviderAVCryptoMockSuccess(ProviderAlphaVantageCrypto):
    async def download_raw_tickers(self) -> csv_table:
        path = Path(__file__).parent / "_mock_data" / "provider_av_crypto_mock_success_tickers.csv"
        with path.open() as file:
            csv_table = csv.reader(file.read().splitlines(), delimiter=",")
        next(csv_table)  # skip table header
        return list(csv_table)

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        return df_quotes_crypto()

    async def healthcheck(self) -> bool:
        return True


class ProviderAVStocksMockFailureBroken(ProviderAlphaVantageStocks):
    _tickers: ClassVar[dict[str, Ticker]] = {}

    async def download_raw_tickers(self) -> csv_table:
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
    _tickers: ClassVar[dict[str, Ticker]] = {}

    async def download_raw_tickers(self) -> csv_table:
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
    _tickers: ClassVar[dict[str, Ticker]] = {}

    async def download_raw_tickers(self) -> csv_table:
        return []

    async def _download_data(self, ticker: Ticker, timeframe: SessionTimeframe) -> pd.DataFrame:
        mock_data_raw: dict[str, list] = {}
        return pd.DataFrame.from_dict(mock_data_raw)


class ProviderAVCryptoMockFailureBlank(ProviderAlphaVantageCrypto):
    _tickers: ClassVar[dict[str, Ticker]] = {}

    async def download_raw_tickers(self) -> csv_table:
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
