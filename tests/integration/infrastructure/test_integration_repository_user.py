from unittest import IsolatedAsyncioTestCase

from flash_backend.app.domain.user import User, UserStatus
from flash_backend.app.infrastructure.db import AsyncSessionFactory
from flash_backend.app.infrastructure.repositories.user import RepositoryUserSQL


class TestRepositoryUserSQL(IsolatedAsyncioTestCase):
    async def test_complete(self) -> None:
        async with AsyncSessionFactory() as db_session:
            repository = RepositoryUserSQL(db_session)
            test_user = User(
                email="test-signup@alekseisemenov.ru",
                name="test-signup",
                password="uc8a&Q!W",  # noqa: S106
                status=UserStatus.active,
            )
            repository.add(test_user)
            await repository.flush()

            # Get by email
            user_by_email = await repository.get_by_email(test_user.email)
            assert user_by_email, "User not found"
            assert user_by_email.email == test_user.email, "User user returned"
            assert user_by_email.id, "User id not set"
            assert user_by_email.datetime_create, "Creation datetime not set"
            assert user_by_email.status.value == test_user.status.value, "Wrong user status (enum)"

            # Get by id
            user_by_id = await repository.get_by_id(user_by_email.id)
            assert user_by_id, "User not found"
