from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute, QueryableAttribute
from sqlalchemy.orm.dynamic import AppenderQuery
from uuid6 import uuid6

from app.domain.iteration import DomainIteration
from app.domain.session import DomainSession
from app.domain.user import DomainAuth, DomainUser
from app.infrastructure.nosql import DbNoSql, DbNoSqlMongo
from app.infrastructure.repositories.identity_map import IdentityMapSqlAlchemy
from app.infrastructure.repositories.iteration import RepositoryNoSqlIteration
from app.infrastructure.repositories.session import RepositorySessionSql
from app.infrastructure.repositories.user import RepositoryUserSql
from app.infrastructure.sql import DbSql, DbSqlPg
from app.system.constants import AuthStatus
from app.system.exceptions import DbObjectNotFoundError

RepositoryUserSqlWithUser = Callable[
    [AsyncSession, DomainUser], Coroutine[Any, Any, RepositoryUserSql]
]


@pytest.fixture()
def db_sql() -> DbSql:
    return DbSqlPg()


@pytest.fixture()
def db_nosql() -> DbNoSql:
    return DbNoSqlMongo()


@pytest.fixture()
def user_repository_with_user() -> RepositoryUserSqlWithUser:
    async def create_repository(
        db_session: AsyncSession, user_domain: DomainUser
    ) -> RepositoryUserSql:
        """Create SQL repository and add user inside"""
        repository_user = RepositoryUserSql(db_session, IdentityMapSqlAlchemy)
        repository_user.add(user_domain)
        await repository_user.flush()
        return repository_user

    return create_repository


class TestRepositorySql:
    def test_identity_map(self, user_domain: DomainUser, db_sql: DbSql) -> None:
        """Chech if identity map works as expected"""

        identity_map = IdentityMapSqlAlchemy()
        if not isinstance(DomainUser.email, InstrumentedAttribute | QueryableAttribute):
            pytest.fail("Domain model is not mapped with ORM")
        if not isinstance(user_domain.auths, AppenderQuery):
            pytest.fail("Domain model relationships is not supported by ORM mapper")

        # Test entities identity map
        identity_map.entities.add(user_domain)
        user_from_im_entities = identity_map.entities.get(DomainUser, user_domain._id)
        assert user_domain == user_from_im_entities, "Entities identity map works incorrectly"

        # Test sql queries identity map
        identity_map.queries.add(DomainUser.email, user_domain.email, [user_domain])  # type: ignore[arg-type]
        user_from_im_queries = identity_map.queries.get(DomainUser.email, user_domain.email)  # type: ignore[arg-type]
        assert [user_domain] == user_from_im_queries, "Queries identity map works incorrectly"

        # Test sql relationships identity map
        auth_domain = DomainAuth(
            ip_address="127.0.0.1",
            http_user_agent="Test",
            status=AuthStatus.sign_in,
            user=user_domain,
        )
        identity_map.relationships.add(user_domain.auths, [auth_domain])  # type: ignore[arg-type]
        auths_from_im_relationships = identity_map.relationships.get(user_domain.auths)  # type: ignore[arg-type]
        assert len(auths_from_im_relationships) == 1, "Relationships identity map works incorrectly"

    @pytest.mark.asyncio()
    async def test_repository_user(
        self,
        user_domain: DomainUser,
        user_repository_with_user: RepositoryUserSqlWithUser,
        db_sql: DbSql,
    ) -> None:
        """Check if it is possible to create single db object using domain model"""

        async with db_sql.get_session() as db_session:
            # Add user
            repository_user = await user_repository_with_user(db_session, user_domain)

            # Get by email
            user_from_repo_by_email = await repository_user.get_by_email(user_domain.email.value)
            assert user_from_repo_by_email, "User not found"
            assert user_domain == user_from_repo_by_email, "Domain user is not the same as from db"

            # Raise error if try to get user by wrong email
            wrong_email = "wrong@email.com"
            with pytest.raises(DbObjectNotFoundError):
                user_from_repo_by_email = await repository_user.get_by_email(wrong_email)

            # Get by id
            user_from_repo_by_id = await repository_user.get_by_id(user_from_repo_by_email._id)
            assert user_from_repo_by_id, "User not found"
            assert user_domain == user_from_repo_by_id, "Domain user is not the same as from db"

    @pytest.mark.asyncio()
    async def test_repository_user_auths(
        self,
        user_domain: DomainUser,
        user_repository_with_user: RepositoryUserSqlWithUser,
        db_sql: DbSql,
    ) -> None:
        """Check if it is possible to create multiple db objects using domain models"""

        async with db_sql.get_session() as db_session:
            repository_user = await user_repository_with_user(db_session, user_domain)
            user_from_repo = await repository_user.get_by_email(user_domain.email.value)
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
            assert auths_repo[0]._id, "Auth id not set"
            assert auths_repo[0].status.value == auth_domain_sign_up.status.value, "Wrong status"

    @pytest.mark.asyncio()
    async def test_repository_session(self, session: DomainSession, db_sql: DbSql) -> None:
        """Check if it is possible to create single db object using domain model"""
        async with db_sql.get_session() as db_session:
            repository_session = RepositorySessionSql(db_session)
            repository_session.add(session)
            await repository_session.flush()
            assert session._id
            session_from_db = await repository_session.get_by_id(session._id)
            assert session_from_db.ticker == session.ticker


class TestRepositoryNoSql:
    def test_repository_iteration_quotes(self, db_nosql: DbNoSql, session: DomainSession) -> None:
        repository = RepositoryNoSqlIteration(db_nosql)  # type: ignore[arg-type]

        # Create and record iterations
        current_file_path = Path(__file__).parent.parent.parent
        data_path = current_file_path / "_mock_data" / "mock_iteration_01.json"
        mock_data_raw = pd.read_json(data_path)
        mock_session_id = uuid6()
        for iter_num in range(2):
            iteration = DomainIteration(
                session_id=mock_session_id,
                iteration_num=iter_num,
                df_quotes=pd.DataFrame.from_dict(mock_data_raw),
                session=session,
            )
            repository.add(iteration)

        # Get an iteration collection from repository
        iteration_col_from_repo = repository.get_iteration_collection(mock_session_id)
        assert len(iteration_col_from_repo) == 2
        assert iteration_col_from_repo[0].session_id == mock_session_id
        assert not iteration_col_from_repo[0].df_quotes.empty

        # Get a single iteration from repository
        iteration_from_repo = repository.get_iteration(mock_session_id, 1)
        assert iteration_from_repo.session_id == mock_session_id
        assert not iteration_from_repo.df_quotes.empty
