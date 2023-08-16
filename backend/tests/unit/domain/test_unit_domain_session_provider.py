import pytest
import structlog

from app.domain.session_provider import Provider, Ticker
from app.system.constants import SessionTimeframe
from app.system.exceptions import ProviderAccessError, ProviderInvalidDataError
from app.system.logger import configure_logger
from tests.unit.mock_session_providers import (
    provider_av_crypto_mock_blank,
    provider_av_crypto_mock_broken,
    provider_av_crypto_mock_success,
    provider_av_stocks_mock_blank,
    provider_av_stocks_mock_broken,
    provider_av_stocks_mock_success,
)

configure_logger()


class TestProviderAlphaVantage:
    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        "provider", [provider_av_stocks_mock_success, provider_av_crypto_mock_success]
    )
    async def test_get_list_success(self, provider: Provider) -> None:
        raw_tickers = await provider.ticker_col._download_raw_tickers()
        stocks = provider.ticker_col._process_tickers(raw_tickers)
        assert len(stocks) > 0
        assert isinstance(list(stocks.values())[0], Ticker)

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        "provider", [provider_av_stocks_mock_blank, provider_av_crypto_mock_blank]
    )
    async def test_get_list_failure_blank(self, provider: Provider) -> None:
        raw_tickers = await provider.ticker_col._download_raw_tickers()
        with structlog.testing.capture_logs() as logs:
            provider.ticker_col._process_tickers(raw_tickers)
        assert len(logs) == 1
        assert logs[0]["error"] == ProviderAccessError.msg

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        "provider", [provider_av_stocks_mock_broken, provider_av_crypto_mock_broken]
    )
    async def test_get_list_failure_broken(self, provider: Provider) -> None:
        raw_tickers = await provider.ticker_col._download_raw_tickers()
        with structlog.testing.capture_logs() as logs:
            provider.ticker_col._process_tickers(raw_tickers)
        assert len(logs) == 1
        assert logs[0]["error"] == ProviderInvalidDataError.msg

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        "provider", [provider_av_stocks_mock_success, provider_av_crypto_mock_success]
    )
    async def test_get_data_success(self, provider: Provider, mock_ticker: Ticker) -> None:
        df_quotes = await provider.get_data(ticker=mock_ticker, timeframe=SessionTimeframe.daily)
        assert len(df_quotes) > 0

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        "provider", [provider_av_stocks_mock_blank, provider_av_crypto_mock_blank]
    )
    async def test_get_data_fauilure_blank(self, provider: Provider, mock_ticker: Ticker) -> None:
        with pytest.raises(ProviderInvalidDataError):
            await provider.get_data(ticker=mock_ticker, timeframe=SessionTimeframe.daily)

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        "provider", [provider_av_stocks_mock_broken, provider_av_crypto_mock_broken]
    )
    async def test_get_data_fauilure_broken(self, provider: Provider, mock_ticker: Ticker) -> None:
        with pytest.raises(ProviderInvalidDataError):
            await provider.get_data(ticker=mock_ticker, timeframe=SessionTimeframe.daily)
