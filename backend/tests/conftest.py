import uuid

import pytest

from app.api.schemas.user import ReqSignIn, ReqSignUp
from app.domain.session_provider import (
    ProviderAlphaVantageCrypto,
    ProviderAlphaVantageStocks,
    csv_table,
)
from app.domain.user import DomainUser
from app.system.constants import UserStatus


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


class ProviderAVStocksMockSuccess(ProviderAlphaVantageStocks):
    def _download_csv(self) -> csv_table:
        return [
            ["MSFT", "Microsoft Corp", "NASDAQ", "Stock", "13.03.1986", "null", "Active"],
            ["AAPL", "Apple Inc", "NASDAQ", "Stock", "12.12.1980", "null", "Active"],
            ["BA", "Boeing Company", "NYSE", "Stock", "02.01.1962", "null", "Active"],
        ]


class ProviderAVCryptoMockSuccess(ProviderAlphaVantageCrypto):
    def _download_csv(self) -> csv_table:
        return [["BTC", "Bitcoin"], ["ETH", "Ethereum"]]


class ProviderAVStocksMockFailureBrokenTicker(ProviderAlphaVantageStocks):
    def _download_csv(self) -> csv_table:
        return [
            ["", "", "NASDAQ", "Stock", "13.03.1986", "null", "Active"],
            ["AAPL", "Apple Inc", "NASDAQ", "Stock", "12.12.1980", "null", "Active"],
        ]


class ProviderAVCryptoMockFailureBrokenTicker(ProviderAlphaVantageCrypto):
    def _download_csv(self) -> csv_table:
        return [["", "Bitcoin"], ["ETH", "Ethereum"]]


class ProviderAVStocksMockFailureBlank(ProviderAlphaVantageStocks):
    def _download_csv(self) -> csv_table:
        return []


class ProviderAlVCryptoMockFailureBlank(ProviderAlphaVantageCrypto):
    def _download_csv(self) -> csv_table:
        return []
