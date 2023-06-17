from copy import copy

import pytest
import pytest_asyncio
from jose import jwt

from app.domain.user import DomainUser
from app.services.user import JwtTokenEncoded, ServiceUser
from app.services.user_authorization import ServiceAuthorization, verify_authorization
from app.system.config import settings
from app.system.exceptions import InvalidJwtError, JwtExpiredError
from tests.unit.services.conftest import UnitOfWorkUserFake

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture()
async def token_encoded(service_user: ServiceUser, user_sign_up: DomainUser) -> JwtTokenEncoded:
    token = await service_user.create_access_token(user_sign_up)
    return token


@pytest_asyncio.fixture()
async def service_auth(
    token_encoded: JwtTokenEncoded, uow_user: UnitOfWorkUserFake
) -> ServiceAuthorization:
    return ServiceAuthorization(token_encoded.access_token, uow_user)  # type: ignore[arg-type]


class TestServiceAuthorization:
    async def test_authorization_success(
        self, service_auth: ServiceAuthorization, user_sign_up: DomainUser
    ) -> None:
        user_by_token = await service_auth.get_current_user()
        assert user_by_token == user_sign_up

    async def test_authorization_failure_invalid(
        self, token_encoded: JwtTokenEncoded, uow_user: UnitOfWorkUserFake
    ) -> None:
        token_encoded_invalid = token_encoded.access_token + "wrong"
        with pytest.raises(InvalidJwtError):
            ServiceAuthorization(token_encoded_invalid, uow_user)  # type: ignore[arg-type]

    async def test_authorization_failure_expired(
        self, token_encoded: JwtTokenEncoded, uow_user: UnitOfWorkUserFake
    ) -> None:
        token_encoded_valid = token_encoded.access_token
        token_decoded_valid = jwt.decode(token=token_encoded_valid, key=settings.JWT_SECRET_KEY)
        token_decoded_invalid = copy(token_decoded_valid)
        token_decoded_invalid["exp"] = token_decoded_invalid["iat"] - 100
        token_encoded_invalid = jwt.encode(
            token_decoded_invalid, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        )
        with pytest.raises(JwtExpiredError):
            ServiceAuthorization(token_encoded_invalid, uow_user)  # type: ignore[arg-type]

    async def test_verify_authorization(
        self, token_encoded: JwtTokenEncoded, uow_user: UnitOfWorkUserFake
    ) -> None:
        service_auth_gen = verify_authorization(token_encoded.access_token, uow_user)  # type: ignore[arg-type]
        service_auth = await anext(service_auth_gen)
        assert isinstance(service_auth, ServiceAuthorization)
        assert isinstance(service_auth.user, DomainUser)
