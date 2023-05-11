from unittest import IsolatedAsyncioTestCase

from sqlalchemy.ext.asyncio import AsyncSession

from flash_backend.app.domain.auth import AuthStatus, DomainAuth
from flash_backend.app.domain.user import DomainUser, UserStatus
from flash_backend.app.infrastructure.db import get_new_engine, get_sessionmaker
from flash_backend.app.infrastructure.repositories.auth import RepositoryAuthSQL
from flash_backend.app.infrastructure.repositories.user import RepositoryUserSQL


class TestRepositorySQL(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        """IsolatedAsyncioTestCases require for indvidual engines for each test"""
        self.engine = get_new_engine()
        self.sessionmaker = get_sessionmaker(self.engine)

    @staticmethod
    def _create_test_user() -> DomainUser:
        test_user = DomainUser(
            email="test-signup@alekseisemenov.ru",
            name="test-signup",
            password="uc8a&Q!W",  # noqa: S106
            status=UserStatus.active,
        )
        return test_user

    @staticmethod
    async def _create_user_repository(
        db_session: AsyncSession, user: DomainUser
    ) -> RepositoryUserSQL:
        """Create SQL repository and add user inside"""
        repository_user = RepositoryUserSQL(db_session)
        repository_user.add(user)
        await repository_user.flush()
        return repository_user

    async def test_repository_auth(self) -> None:
        """Check if it is possible to create db objects using domain models using SQL repository"""
        async with self.sessionmaker() as db_session:
            user_domain = self._create_test_user()
            repository_user = await self._create_user_repository(db_session, user_domain)
            user_orm = await repository_user.get_by_email(user_domain.email)
            assert user_orm, "User not found"

            # Create auth for new user
            repository_auth = RepositoryAuthSQL(db_session)
            test_auth = DomainAuth(
                user_id=user_orm.id,
                http_user_agent="Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us)",
                ip_address="127.0.0.1",
                status=AuthStatus.sign_up,
            )
            repository_auth.add(test_auth)
            await repository_auth.flush()

            # Get by user
            auth = await repository_auth.get_by_user(user_orm)
            assert auth.id, "Auth id not set"
            assert auth.status.value == test_auth.status.value, "Wrong status (enum)"
            assert auth, "Auth not created"

    async def test_repository_user(self) -> None:
        """Check if it is possible to create db objects using domain models using SQL repository"""
        async with self.sessionmaker() as db_session:
            user_domain = self._create_test_user()
            repository_user = await self._create_user_repository(db_session, user_domain)

            # Get by email
            user_by_email = await repository_user.get_by_email(user_domain.email)
            assert user_by_email, "User not found"
            assert user_by_email.email == user_domain.email, "User with wrong email returned"
            assert user_by_email.id, "User id not set"
            assert user_by_email.datetime_create, "Creation datetime not set"
            assert user_by_email.status.value == user_domain.status.value, "Wrong status (enum)"

            # Get by id
            user_by_id = await repository_user.get_by_id(user_by_email.id)
            assert user_by_id, "User not found"

            await db_session.rollback()

    async def asyncTearDown(self) -> None:
        await self.engine.dispose()
