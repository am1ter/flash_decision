from datetime import datetime
from random import randint
from unittest import IsolatedAsyncioTestCase

from flash_backend.app.api.schemas.user import ReqSignUp
from flash_backend.app.domain.user import User
from flash_backend.app.infrastructure.repositories.base import Repository
from flash_backend.app.services.user import ServiceUser


class RepositoryUserFake(Repository):
    storage: dict[int, User] = {}

    def add(self, user: User) -> None:
        user.id = randint(1, 1000)
        user.datetime_create = datetime.utcnow()
        self.storage[user.id] = user

    async def save(self) -> None:
        pass

    async def get_by_id(self, id: int) -> User:
        return self.storage[id]

    async def get_by_email(self, email: str) -> User | None:
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
