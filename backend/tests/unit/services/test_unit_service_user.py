from copy import copy
from datetime import datetime
from random import randint
from unittest import IsolatedAsyncioTestCase

from jose import jwt

from app.api.schemas.user import ReqSignIn, ReqSignUp, ReqSystemInfo
from app.bootstrap import Bootstrap
from app.domain.user import DomainAuth, DomainUser
from app.infrastructure.repositories.base import Repository
from app.infrastructure.units_of_work.base import UnitOfWork
from app.services.user import ServiceUser
from app.system.config import settings
from app.system.constants import UserStatus
from app.system.exceptions import (
    EmailValidationError,
    IpAddressValidationError,
    UserDisabledError,
    WrongPasswordError,
)


class RepositoryUserFake(Repository):
    def __init__(self) -> None:
        self.storage_user: dict[int, DomainUser] = {}
        self.storage_auth: dict[int, list[DomainAuth]] = {}

    def add(self, obj: DomainUser) -> None:  # type: ignore[override]
        obj.id = randint(1, 1000)
        obj.datetime_create = datetime.utcnow()
        self.storage_user[obj.id] = obj
        self.storage_auth[obj.id] = list(obj.auths)

    async def save(self) -> None:
        pass

    async def flush(self) -> None:
        pass

    async def refresh(self, object: DomainUser) -> None:
        pass

    async def get_by_id(self, id: int) -> DomainUser:
        return self.storage_user[id]

    async def get_by_email(self, email: str) -> DomainUser | None:
        user = [v for v in self.storage_user.values() if v.email.value == email]
        return user[0]


class UnitOfWorkUserFake(UnitOfWork):
    def __init__(self) -> None:
        self.repository = RepositoryUserFake()

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


class TestServiceUser(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.bootstrap = Bootstrap(start_orm=True)
        self.uow = UnitOfWorkUserFake()
        self.service = ServiceUser(uow=self.uow)  # type: ignore[arg-type]
        self.req_sign_up = ReqSignUp(
            email="test-signup@alekseisemenov.ru",
            name="test-signup",
            password="uc8a&Q!W",  # noqa: S106
        )
        self.req_sign_in = ReqSignIn(
            username=self.req_sign_up.email, password=self.req_sign_up.password
        )
        self.req_system_info = ReqSystemInfo(ip_address="127.0.0.1", user_agent="Test")

    async def test_sign_up_success(self) -> None:
        user = await self.service.sign_up(self.req_sign_up, self.req_system_info)

        # Check user
        self.assertIsNotNone(user, "New user not created")
        self.assertEqual(self.req_sign_up.email, user.email.value)
        self.assertEqual(self.req_sign_up.name, user.name)

        # Check password
        self.assertNotEqual(
            self.req_sign_up.password, user.password.value, "Password is not hashed"
        )
        self.assertTrue(
            user.password.verify_password(self.req_sign_up.password), "Password hashed incorrectly"
        )

        # Check auth
        self.assertEqual(len(self.uow.repository.storage_auth), 1, "Auth not created")

    async def test_sign_up_failure_wrong_email(self) -> None:
        req_sign_up_wrong_email = copy(self.req_sign_up)
        req_sign_up_wrong_email.email = "wrong@wrong"
        with self.assertRaises(EmailValidationError):
            await self.service.sign_up(req_sign_up_wrong_email, self.req_system_info)

    async def test_sign_in_success(self) -> None:
        user_sign_up = await self.service.sign_up(self.req_sign_up, self.req_system_info)
        user_sign_in = await self.service.sign_in(self.req_sign_in, self.req_system_info)

        # Check user signed in
        self.assertEqual(user_sign_up, user_sign_in)

        # Check auth record created
        sign_in_auths = self.uow.repository.storage_auth[user_sign_up.id]
        self.assertEqual(len(sign_in_auths), 2, "Auths not created")
        self.assertEqual(sign_in_auths[0].user, user_sign_in, "Auths for sign in not created")

    async def test_sign_in_failure_user_disabled(self) -> None:
        user_sign_up = await self.service.sign_up(self.req_sign_up, self.req_system_info)
        self.assertIsNotNone(user_sign_up, "User is not created")
        user_sign_up.status = UserStatus.disabled
        with self.assertRaises(UserDisabledError):
            await self.service.sign_in(self.req_sign_in, self.req_system_info)
        user_sign_up.status = UserStatus.active

    async def test_sign_in_failure_wrong_password(self) -> None:
        user_sign_up = await self.service.sign_up(self.req_sign_up, self.req_system_info)
        self.assertIsNotNone(user_sign_up, "User is not created")
        self.req_sign_in.password = "wrongPass"  # noqa: S105
        with self.assertRaises(WrongPasswordError):
            await self.service.sign_in(self.req_sign_in, self.req_system_info)

    async def test_auth_failure_wrong_ip(self) -> None:
        req_system_info_wrong_ip = copy(self.req_system_info)
        req_system_info_wrong_ip.ip_address = "192.168.0."
        with self.assertRaises(IpAddressValidationError):
            await self.service.sign_up(self.req_sign_up, req_system_info_wrong_ip)

    async def test_create_access_token(self) -> None:
        user = await self.service.sign_up(self.req_sign_up, self.req_system_info)
        token_encoded = await self.service.create_access_token(user)
        token_decoded = jwt.decode(token=token_encoded.access_token, key=settings.JWT_SECRET_KEY)
        self.assertEqual(token_decoded["sub"], user.email.value)
        self.assertGreater(token_decoded["exp"], token_decoded["iat"])
