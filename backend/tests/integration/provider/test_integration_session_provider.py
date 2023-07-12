import pandas as pd
import pytest

from app.domain.session_provider import (
    ProviderAlphaVantageCrypto,
    ProviderAlphaVantageStocks,
    Ticker,
)
from app.system.config import settings
from app.system.constants import SessionTimeframe, TickerType
from app.system.exceptions import ProviderRateLimitExceededError


@pytest.fixture()
def ticker_stocks() -> Ticker:
    return Ticker(ticker_type=TickerType.stock, exchange="NASDAQ", symbol="AAPL", name="Apple Inc")


@pytest.fixture()
def ticker_crypto() -> Ticker:
    return Ticker(ticker_type=TickerType.crypto, exchange="Crypto", symbol="BTC", name="Bitcoin")


class TestProviderAlphaVantageStocks:
    @pytest.mark.asyncio()
    async def test_get_list(self) -> None:
        assert settings.ALPHAVANTAGE_API_KEY_STOCKS
        provider = ProviderAlphaVantageStocks()
        raw_tickers = await provider.download_raw_tickers()
        tickers = provider.process_tickers(raw_tickers)
        if not tickers:
            raise ProviderRateLimitExceededError

    @pytest.mark.asyncio()
    async def test_get_data_intraday(self, ticker_stocks: Ticker) -> None:
        assert settings.ALPHAVANTAGE_API_KEY_STOCKS
        provider = ProviderAlphaVantageStocks()
        data = await provider.get_data(ticker_stocks, SessionTimeframe.minutes5)
        assert isinstance(data, pd.DataFrame)
        assert not data.empty

    @pytest.mark.asyncio()
    async def test_get_data_daily(self, ticker_stocks: Ticker) -> None:
        assert settings.ALPHAVANTAGE_API_KEY_STOCKS
        provider = ProviderAlphaVantageStocks()
        data = await provider.get_data(ticker_stocks, SessionTimeframe.daily)
        assert isinstance(data, pd.DataFrame)
        assert not data.empty


class TestProviderAlphaVantageCrypto:
    @pytest.mark.asyncio()
    async def test_get_list(self) -> None:
        assert settings.ALPHAVANTAGE_API_KEY_CRYPTO
        provider = ProviderAlphaVantageCrypto()
        raw_tickers = await provider.download_raw_tickers()
        tickers = provider.process_tickers(raw_tickers)
        if not tickers:
            raise ProviderRateLimitExceededError

    @pytest.mark.asyncio()
    async def test_get_data_intraday(self, ticker_crypto: Ticker) -> None:
        assert settings.ALPHAVANTAGE_API_KEY_CRYPTO
        provider = ProviderAlphaVantageCrypto()
        data = await provider.get_data(ticker_crypto, SessionTimeframe.daily)
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
