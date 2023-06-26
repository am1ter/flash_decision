from collections.abc import Callable

import pytest
import structlog

from app.domain.session_provider import (
    ProviderAlphaVantage,
    ProviderAlphaVantageCrypto,
    ProviderAlphaVantageStocks,
    Ticker,
    csv_table,
)
from app.system.exceptions import ProviderAccessError, ProviderInvalidDataError

prov_av_stocks = ProviderAlphaVantageStocks
prov_av_crypto = ProviderAlphaVantageCrypto


def download_csv_mock_stocks(*args) -> csv_table:
    return [
        ["MSFT", "Microsoft Corp", "NASDAQ", "Stock", "13.03.1986", "null", "Active"],
        ["AAPL", "Apple Inc", "NASDAQ", "Stock", "12.12.1980", "null", "Active"],
        ["BA", "Boeing Company", "NYSE", "Stock", "02.01.1962", "null", "Active"],
    ]


def download_csv_mock_broken_ticker_stocks(*args) -> csv_table:
    return [
        ["", "", "NASDAQ", "Stock", "13.03.1986", "null", "Active"],
        ["AAPL", "Apple Inc", "NASDAQ", "Stock", "12.12.1980", "null", "Active"],
    ]


def download_csv_mock_crypto(*args) -> csv_table:
    return [["BTC", "Bitcoin"], ["ETH", "Ethereum"]]


def download_csv_mock_broken_ticker_crypto(*args) -> csv_table:
    return [["", "Bitcoin"], ["ETH", "Ethereum"]]


class TestProviderAlphaVantage:
    def _download_csv_mock_blank(self) -> csv_table:
        return []

    @pytest.mark.parametrize(
        ("provider_class", "download_csv_mock"),
        [(prov_av_stocks, download_csv_mock_stocks), (prov_av_crypto, download_csv_mock_crypto)],
    )
    def test_get_list_success(
        self,
        provider_class: type[ProviderAlphaVantage],
        download_csv_mock: Callable[[], csv_table],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(provider_class, "_download_csv", download_csv_mock)
        provider = provider_class()
        stocks = provider.get_list()
        assert len(stocks) == len(download_csv_mock())
        assert isinstance(stocks[0], Ticker)

    @pytest.mark.parametrize("provider_class", [prov_av_stocks, prov_av_crypto])
    def test_get_list_failure_blank(
        self,
        provider_class: type[ProviderAlphaVantage],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(provider_class, "_download_csv", self._download_csv_mock_blank)
        provider = provider_class()
        with structlog.testing.capture_logs() as logs:
            provider.get_list()
        assert len(logs) == 1
        assert logs[0]["exc_info"].msg == ProviderAccessError.msg

    @pytest.mark.parametrize(
        ("provider_class", "download_csv_mock_broken_ticker"),
        [
            (prov_av_stocks, download_csv_mock_broken_ticker_stocks),
            (prov_av_crypto, download_csv_mock_broken_ticker_crypto),
        ],
    )
    def test_get_list_failure_broken_ticket(
        self,
        provider_class: type[ProviderAlphaVantage],
        download_csv_mock_broken_ticker: Callable[[], csv_table],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(provider_class, "_download_csv", download_csv_mock_broken_ticker)
        provider = provider_class()
        with structlog.testing.capture_logs() as logs:
            provider.get_list()
        assert len(logs) == 1
        assert logs[0]["event"] == ProviderInvalidDataError.msg
