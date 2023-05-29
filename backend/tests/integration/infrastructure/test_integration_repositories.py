from unittest import IsolatedAsyncioTestCase

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.dynamic import AppenderQuery

from app.domain.user import DomainAuth, DomainUser
from app.infrastructure.db import get_new_engine, get_sessionmaker
from app.infrastructure.repositories.identity_map import IdentityMapSQLAlchemy
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
        identity_map = IdentityMapSQLAlchemy()
        repository_user = RepositoryUserSQL(db_session, identity_map)
        repository_user.add(user)
        await repository_user.flush()
        return repository_user

    def test_identity_map(self) -> None:
        """Chech if identity map works as expected"""

        identity_map = IdentityMapSQLAlchemy()
        user_domain = self._create_test_user()
        if not isinstance(DomainUser.email, InstrumentedAttribute):
            self.fail("Domain model is not mapped with ORM")
        if not isinstance(user_domain.auths, AppenderQuery):
            self.fail("Domain model relationships is not supported by ORM mapper")

        # Test entities identity map
        identity_map.entities.add(user_domain)
        user_from_im_entities = identity_map.entities.get(DomainUser, user_domain.id)
        assert user_domain == user_from_im_entities, "Entities identity map works incorrectly"

        # Test sql queries identity map
        identity_map.queries.add(DomainUser.email, user_domain.email, [user_domain])
        user_from_im_queries = identity_map.queries.get(DomainUser.email, user_domain.email)
        assert [user_domain] == user_from_im_queries, "Queries identity map works incorrectly"

        # Test sql relationships identity map
        auth_domain = DomainAuth(
            ip_address="127.0.0.1",
            http_user_agent="Test",
            status=AuthStatus.sign_in,
            user=user_domain,
        )
        identity_map.relationships.add(user_domain.auths, [auth_domain])
        auths_from_im_relationships = identity_map.relationships.get(user_domain.auths)
        assert len(auths_from_im_relationships) == 1, "Relationships identity map works incorrectly"

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

            # Get auth by user
            await repository_user.refresh(user_from_repo)
            auths_repo = await repository_user.load_relationship(user_from_repo.auths)
            assert auths_repo, "Auth not created"
            assert len(auths_repo) == 2, "Auths do not inserted correctly"
            assert isinstance(auths_repo[0], DomainAuth), "Auth has wrong type"
            assert auths_repo[0].id, "Auth id not set"
            assert auths_repo[0].status.value == auth_domain_sign_up.status.value, "Wrong status"

    async def asyncTearDown(self) -> None:
        await self.engine.dispose()
