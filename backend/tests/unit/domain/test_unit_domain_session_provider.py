import pytest
import structlog

from app.domain.session_provider import Provider, Ticker
from app.system.exceptions import ProviderAccessError, ProviderInvalidDataError
from tests.conftest import (
    ProviderAlVCryptoMockFailureBlank,
    ProviderAVCryptoMockFailureBrokenTicker,
    ProviderAVCryptoMockSuccess,
    ProviderAVStocksMockFailureBlank,
    ProviderAVStocksMockFailureBrokenTicker,
    ProviderAVStocksMockSuccess,
)


class TestProviderAlphaVantage:
    @pytest.mark.parametrize(
        "provider_cls",
        [ProviderAVStocksMockSuccess, ProviderAVCryptoMockSuccess],
    )
    def test_get_list_success(self, provider_cls: type[Provider]) -> None:
        provider = provider_cls()
        stocks = provider.get_list()
        assert len(stocks) > 0
        assert isinstance(stocks[0], Ticker)

    @pytest.mark.parametrize(
        "provider_cls",
        [ProviderAVStocksMockFailureBlank, ProviderAlVCryptoMockFailureBlank],
    )
    def test_get_list_failure_blank(self, provider_cls: type[Provider]) -> None:
        provider = provider_cls()
        with structlog.testing.capture_logs() as logs:
            provider.get_list()
        assert len(logs) == 1
        assert logs[0]["exc_info"].msg == ProviderAccessError.msg

    @pytest.mark.parametrize(
        "provider_cls",
        [ProviderAVStocksMockFailureBrokenTicker, ProviderAVCryptoMockFailureBrokenTicker],
    )
    def test_get_list_failure_broken_ticket(self, provider_cls: type[Provider]) -> None:
        provider = provider_cls()
        with structlog.testing.capture_logs() as logs:
            provider.get_list()
        assert len(logs) == 1
        assert logs[0]["event"] == ProviderInvalidDataError.msg
