from unittest import IsolatedAsyncioTestCase

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user import DomainAuth, DomainUser
from app.infrastructure.db import get_new_engine, get_sessionmaker
from app.infrastructure.repositories.user import RepositoryUserSQL
from app.system.constants import AuthStatus, UserStatus
from app.system.exceptions import DbObjectNotFoundError


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
    async def _create_user_repository_with_user(
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
            # Add user
            user_domain = self._create_test_user()
            repository_user = await self._create_user_repository_with_user(db_session, user_domain)

            # Get by email
            user_from_repo_by_email = await repository_user.get_by_email(user_domain.email)
            assert user_from_repo_by_email, "User not found"
            assert user_domain == user_from_repo_by_email, "Domain user is not the same as from db"

            # Raise error if try to get user by wrong email
            wrong_email = "wrong@email.com"
            with self.assertRaises(DbObjectNotFoundError):
                user_from_repo_by_email = await repository_user.get_by_email(wrong_email)

            # Get by id
            user_from_repo_by_id = await repository_user.get_by_id(user_from_repo_by_email.id)
            assert user_from_repo_by_id, "User not found"
            assert user_domain == user_from_repo_by_id, "Domain user is not the same as from db"

    async def test_repository_user_auths(self) -> None:
        """Check if it is possible to create multiple db objects using domain models"""

        async with self.sessionmaker() as db_session:
            user_domain = self._create_test_user()
            repository_user = await self._create_user_repository_with_user(db_session, user_domain)
            user_from_repo = await repository_user.get_by_email(user_domain.email)
            assert user_from_repo, "User not found"

            # Create auth for new user and add it to repo directly
            auth_domain_sign_up = DomainAuth(
                user=user_domain,
                http_user_agent="Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us)",
                ip_address="127.0.0.1",
                status=AuthStatus.sign_up,
            )
            repository_user.add(auth_domain_sign_up)

            # Create auth for new user and add it it repo automatically using relationship
            DomainAuth(
                user=user_domain,
                http_user_agent="Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us)",
                ip_address="127.0.0.1",
                status=AuthStatus.sign_in,
            )
            repository_user.add(user_from_repo)
            await repository_user.flush()

            # Get by user
            await repository_user.refresh(user_from_repo)
            auths_repo = await repository_user.load_relationship(user_from_repo.auths)
            assert auths_repo, "Auth not created"
            assert len(auths_repo) == 2, "Auths do not inserted correctly"
            assert isinstance(auths_repo[0], DomainAuth), "Auth has wrong type"
            assert auths_repo[0].id, "Auth id not set"
            assert auths_repo[0].status.value == auth_domain_sign_up.status.value, "Wrong status"

    async def asyncTearDown(self) -> None:
        await self.engine.dispose()
