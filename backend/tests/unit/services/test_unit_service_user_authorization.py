from copy import copy
from unittest import IsolatedAsyncioTestCase

from jose import jwt

from app.api.schemas.user import ReqSignUp, ReqSystemInfo
from app.domain.user import DomainUser
from app.services.user import ServiceUser
from app.services.user_authorization import ServiceAuthorization, verify_authorization
from app.system.config import settings
from app.system.exceptions import InvalidJwtError, JwtExpiredError
from tests.unit.services.test_unit_service_user import UnitOfWorkUserFake


class TestServiceAuthorization(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.uow = UnitOfWorkUserFake()
        self.service_user = ServiceUser(uow=self.uow)  # type: ignore[arg-type]
        req_sign_up = ReqSignUp(
            email="test-signup@alekseisemenov.ru",
            name="test-signup",
            password="uc8a&Q!W",  # noqa: S106
        )
        req_system_info = ReqSystemInfo(ip_address="127.0.0.1", user_agent="Test")
        self.user_sign_up = await self.service_user.sign_up(req_sign_up, req_system_info)
        self.token_encoded = await self.service_user.create_access_token(self.user_sign_up)

    async def test_authorization_success(self) -> None:
        self.service_auth = ServiceAuthorization(self.token_encoded.access_token, self.uow)  # type: ignore[arg-type]
        user_by_token = await self.service_auth.get_current_user()
        self.assertEqual(user_by_token, self.user_sign_up)

    async def test_authorization_failure_invalid(self) -> None:
        token_encoded_invalid = self.token_encoded.access_token + "wrong"
        with self.assertRaises(InvalidJwtError):
            self.service_auth = ServiceAuthorization(token_encoded_invalid, self.uow)  # type: ignore[arg-type]

    async def test_authorization_failure_expired(self) -> None:
        token_encoded_valid = self.token_encoded.access_token
        token_decoded_valid = jwt.decode(token=token_encoded_valid, key=settings.JWT_SECRET_KEY)
        token_decoded_invalid = copy(token_decoded_valid)
        token_decoded_invalid["exp"] = token_decoded_invalid["iat"] - 100
        token_encoded_invalid = jwt.encode(
            token_decoded_invalid, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        )
        with self.assertRaises(JwtExpiredError):
            self.service_auth = ServiceAuthorization(token_encoded_invalid, self.uow)  # type: ignore[arg-type]

    async def test_verify_authorization(self) -> None:
        service_auth_gen = verify_authorization(self.token_encoded.access_token, self.uow)  # type: ignore[arg-type]
        service_auth = await anext(service_auth_gen)  # type: ignore[call-overload]
        self.assertTrue(isinstance(service_auth, ServiceAuthorization))
        self.assertTrue(isinstance(service_auth.user, DomainUser))
