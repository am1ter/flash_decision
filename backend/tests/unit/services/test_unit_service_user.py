from datetime import datetime
from random import randint
from unittest import IsolatedAsyncioTestCase

from app.api.schemas.user import ReqSignUp, ReqSystemInfo
from app.domain.auth import DomainAuth
from app.domain.user import DomainUser
from app.infrastructure.repositories.base import Repository
from app.services.user import ServiceUser


class RepositoryUserFake(Repository):
    def __init__(self) -> None:
        self.storage_user: dict[int, DomainUser] = {}
        self.storage_auth: dict[int, DomainAuth] = {}
        self.storage = {"DomainUser": self.storage_user, "DomainAuth": self.storage_auth}

    def add(self, obj: DomainUser | DomainAuth) -> None:
        obj.id = randint(1, 1000)
        obj.datetime_create = datetime.utcnow()
        obj_cls = obj.__class__.__name__
        self.storage[obj_cls][obj.id] = obj

    async def save(self) -> None:
        pass

    async def flush(self) -> None:
        pass

    async def refresh(self, object: DomainUser) -> None:
        pass

    async def get_by_id(self, id: int) -> DomainUser:
        return self.storage_user[id]

    async def get_by_email(self, email: str) -> DomainUser | None:
        user = [v for v in self.storage_user.values() if v.email == email]
        return user[0]


class TestServiceUser(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.repository = RepositoryUserFake()
        self.service = ServiceUser(repository=self.repository)
        self.test_request = ReqSignUp(
            email="test-signup@alekseisemenov.ru",
            name="test-signup",
            password="uc8a&Q!W",  # noqa: S106
        )
        self.req_system_info = ReqSystemInfo(ip_address="127.0.0.1", user_agent="Test")

    async def test_sign_up(self) -> None:
        user = await self.service.sign_up(self.test_request, self.req_system_info)

        # Check user
        self.assertIsNotNone(user, "New user not created")
        self.assertEqual(self.test_request.email, user.email)
        self.assertEqual(self.test_request.name, user.name)

        # Check password
        self.assertNotEqual(self.test_request.password, user.password, "Password is not hashed")

        # Check auth
        self.assertEqual(len(self.repository.storage_auth), 1, "Auth not created")

    async def test_sign_in(self) -> None:
        user_sign_up = await self.service.sign_up(self.test_request, self.req_system_info)
        user_sign_in = await self.service.sign_in(self.test_request, self.req_system_info)

        # Check user signed in
        self.assertEqual(user_sign_up, user_sign_in)

        # Check auth record created
        self.assertEqual(len(self.repository.storage_auth), 2, "Auths not created")
        _, sign_in_auth = self.repository.storage_auth.popitem()
        self.assertEqual(sign_in_auth.user, user_sign_in, "Auths for sign in not created")
