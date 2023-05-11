from datetime import datetime
from random import randint
from unittest import IsolatedAsyncioTestCase

from app.api.schemas.user import ReqSignUp
from app.domain.user import DomainUser
from app.infrastructure.repositories.base import Repository
from app.services.user import ServiceUser


class RepositoryUserFake(Repository):
    storage: dict[int, DomainUser] = {}

    def add(self, user: DomainUser) -> None:
        user.id = randint(1, 1000)
        user.datetime_create = datetime.utcnow()
        self.storage[user.id] = user

    async def save(self) -> None:
        pass

    async def get_by_id(self, id: int) -> DomainUser:
        return self.storage[id]

    async def get_by_email(self, email: str) -> DomainUser | None:
        user = {v for v in self.storage.values() if v.email == email}.pop()
        return user


class TestServiceUser(IsolatedAsyncioTestCase):
    async def test_create_user(self) -> None:
        repository = RepositoryUserFake()
        service = ServiceUser(repository=repository)
        req = ReqSignUp(
            email="test-signup@alekseisemenov.ru",
            name="test-signup",
            password="uc8a&Q!W",  # noqa: S106
        )
        await service.create_user(req)
        new_user = await service.get_user_by_request(req)
        # Checks
        assert new_user, "New user not created"
        self.assertEqual(req.email, new_user.email)
        self.assertEqual(req.name, new_user.name)
        self.assertEqual(req.password, new_user.password)
