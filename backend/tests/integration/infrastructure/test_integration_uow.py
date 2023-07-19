import pytest

from app.domain.user import DomainUser
from app.infrastructure.repositories.user import RepositoryUserSQL
from app.infrastructure.sql import DbSqlPg
from app.infrastructure.units_of_work.base_sql import UnitOfWorkSQLAlchemy
from app.system.exceptions import DbObjectCannotBeCreatedError

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def uow() -> UnitOfWorkSQLAlchemy:
    uow = UnitOfWorkSQLAlchemy(RepositoryUserSQL, DbSqlPg())
    return uow


class TestUnitOfWorkSQLAlchemy:
    async def test_uow_user(self, uow: UnitOfWorkSQLAlchemy) -> None:
        async with uow:
            assert uow._db.is_active
            assert uow.repository

    async def test_uow_commit(self, uow: UnitOfWorkSQLAlchemy, user_domain: DomainUser) -> None:
        # Raise error if user with specific email already exists
        async with uow:
            uow._db.add(user_domain)
            await uow.commit()
            uow._db.bind.engine.dispose(close=False)

    async def test_uow_rollback(self, uow: UnitOfWorkSQLAlchemy, user_domain: DomainUser) -> None:
        # Raise error if user with specific email already exists
        async with uow:
            uow._db.add(user_domain)
            await uow.rollback()
        assert len(uow._db.new) == 0

    async def test_raise_error_sql_record_duplicate(
        self, uow: UnitOfWorkSQLAlchemy, user_domain: DomainUser
    ) -> None:
        user_domain_duplicate = DomainUser(
            name=user_domain.name,
            email=user_domain.email.value,
            password=user_domain.password.value,
            status=user_domain.status,
        )
        async with uow:
            uow.repository.add(user_domain)
            uow.repository.add(user_domain_duplicate)
            # Raise error if user with specific email already exists
            with pytest.raises(DbObjectCannotBeCreatedError):
                await uow.commit()
            uow._db.bind.engine.dispose(close=False)
