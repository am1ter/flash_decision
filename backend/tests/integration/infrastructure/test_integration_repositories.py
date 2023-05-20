from unittest import IsolatedAsyncioTestCase

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.auth import DomainAuth
from app.domain.user import DomainUser
from app.infrastructure.db import get_new_engine, get_sessionmaker
from app.infrastructure.repositories.user import RepositoryUserSQL
from app.system.constants import AuthStatus, UserStatus


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

    async def test_repository_user(self) -> None:
        """Check if it is possible to create single db object using domain model"""

        async with self.sessionmaker() as db_session:
            user_domain = self._create_test_user()
            repository_user = await self._create_user_repository(db_session, user_domain)

            # Get by email
            user_repo_by_email = await repository_user.get_by_email(user_domain.email)
            assert user_repo_by_email, "User not found"
            assert user_domain == user_repo_by_email, "Domain user is not the same as user from db"

            # Get by id
            user_repo_by_id = await repository_user.get_by_id(user_repo_by_email.id)
            assert user_repo_by_id, "User not found"
            assert user_domain == user_repo_by_id, "Domain user is not the same as user from db"

    async def test_repository_user_auths(self) -> None:
        """Check if it is possible to create multiple db objects using domain models"""

        async with self.sessionmaker() as db_session:
            user_domain = self._create_test_user()
            repository_user = await self._create_user_repository(db_session, user_domain)
            user_repo = await repository_user.get_by_email(user_domain.email)
            assert user_repo, "User not found"

            # Create auth for new user
            auth_domain_sign_up = DomainAuth(
                user=user_domain,
                http_user_agent="Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us)",
                ip_address="127.0.0.1",
                status=AuthStatus.sign_up,
            )
            auth_domain_sign_in = DomainAuth(
                user=user_domain,
                http_user_agent="Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us)",
                ip_address="127.0.0.1",
                status=AuthStatus.sign_in,
            )
            repository_user.add(auth_domain_sign_up)
            repository_user.add(auth_domain_sign_in)
            await repository_user.flush()

            # Get by user
            await repository_user.refresh(user_repo)
            auths_repo = await repository_user.load_relationship(user_repo.auths)
            assert auths_repo, "Auth not created"
            assert len(auths_repo) == 2, "Auths do not inserted correctly"
            assert auths_repo[0].id, "Auth id not set"
            assert auths_repo[0].status.value == auth_domain_sign_up.status.value, "Wrong status"

    async def asyncTearDown(self) -> None:
        await self.engine.dispose()
