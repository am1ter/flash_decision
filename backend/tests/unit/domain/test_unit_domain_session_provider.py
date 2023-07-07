import pytest
import structlog

from app.domain.session_provider import Provider, Ticker
from app.system.constants import SessionTimeframe
from app.system.exceptions import ProviderAccessError, ProviderInvalidDataError
from tests.conftest import (
    ProviderAVCryptoMockFailureBlank,
    ProviderAVCryptoMockFailureBroken,
    ProviderAVCryptoMockSuccess,
    ProviderAVStocksMockFailureBlank,
    ProviderAVStocksMockFailureBroken,
    ProviderAVStocksMockSuccess,
)


class TestProviderAlphaVantage:
    @pytest.mark.parametrize(
        "provider_cls",
        [ProviderAVStocksMockSuccess, ProviderAVCryptoMockSuccess],
    )
    def test_get_list_success(self, provider_cls: type[Provider]) -> None:
        provider = provider_cls()
        stocks = provider.get_tickers()
        assert len(stocks) > 0
        assert isinstance(list(stocks.values())[0], Ticker)

    @pytest.mark.parametrize(
        "provider_cls",
        [ProviderAVStocksMockFailureBlank, ProviderAVCryptoMockFailureBlank],
    )
    def test_get_list_failure_blank(self, provider_cls: type[Provider]) -> None:
        provider = provider_cls()
        with structlog.testing.capture_logs() as logs:
            provider.get_tickers()
        assert len(logs) == 1
        assert logs[0]["event"] == ProviderAccessError.msg

    @pytest.mark.parametrize(
        "provider_cls",
        [ProviderAVStocksMockFailureBroken, ProviderAVCryptoMockFailureBroken],
    )
    def test_get_list_failure_broken(self, provider_cls: type[Provider]) -> None:
        provider = provider_cls()
        with structlog.testing.capture_logs() as logs:
            provider.get_tickers()
        assert len(logs) == 1
        assert logs[0]["event"] == ProviderInvalidDataError.msg

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        "provider_cls",
        [ProviderAVStocksMockSuccess, ProviderAVCryptoMockSuccess],
    )
    async def test_get_data_success(
        self, provider_cls: type[Provider], mock_ticker: Ticker
    ) -> None:
        provider = provider_cls()
        df_quotes = await provider.get_data(ticker=mock_ticker, timeframe=SessionTimeframe.daily)
        assert len(df_quotes) > 0

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        "provider_cls",
        [ProviderAVStocksMockFailureBlank, ProviderAVCryptoMockFailureBlank],
    )
    async def test_get_data_fauilure_blank(
        self, provider_cls: type[Provider], mock_ticker: Ticker
    ) -> None:
        provider = provider_cls()
        with pytest.raises(ProviderInvalidDataError):
            await provider.get_data(ticker=mock_ticker, timeframe=SessionTimeframe.daily)

    @pytest.mark.asyncio()
    @pytest.mark.parametrize(
        "provider_cls",
        [ProviderAVStocksMockFailureBroken, ProviderAVCryptoMockFailureBroken],
    )
    async def test_get_data_fauilure_broken(
        self, provider_cls: type[Provider], mock_ticker: Ticker
    ) -> None:
        provider = provider_cls()
        with pytest.raises(ProviderInvalidDataError):
            await provider.get_data(ticker=mock_ticker, timeframe=SessionTimeframe.daily)
