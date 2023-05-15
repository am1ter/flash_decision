from datetime import datetime
from random import randint
from unittest import IsolatedAsyncioTestCase

from app.api.schemas.user import ReqSignUp, ReqSystemInfo
from app.domain.auth import DomainAuth
from app.domain.user import DomainUser
from app.infrastructure.repositories.base import Repository
from app.services.user import ServiceUser


class RepositoryUserFake(Repository):
    storage_user: dict[int, DomainUser] = {}
    storage_auth: dict[int, DomainAuth] = {}
    storage = {"DomainUser": storage_user, "DomainAuth": storage_auth}

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
    async def test_create_user(self) -> None:
        # Init dependencies
        repository = RepositoryUserFake()
        service = ServiceUser(repository=repository)

        # Run func
        req = ReqSignUp(
            email="test-signup@alekseisemenov.ru",
            name="test-signup",
            password="uc8a&Q!W",  # noqa: S106
        )
        req_system_info = ReqSystemInfo(ip_address="127.0.0.1", user_agent="Test")
        new_user = await service.create_user(req, req_system_info)

        # Check user
        self.assertIsNotNone(new_user, "New user not created")
        self.assertEqual(req.email, new_user.email)
        self.assertEqual(req.name, new_user.name)
        self.assertEqual(req.password, new_user.password)

        # Check auth
        self.assertEqual(len(repository.storage_auth), 1, "Auths for new user not created")
