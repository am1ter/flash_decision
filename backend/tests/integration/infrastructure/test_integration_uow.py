import pytest

from app.domain.user import DomainUser
from app.infrastructure.repositories.user import RepositoryUserSQL
from app.infrastructure.units_of_work.base_sql import UnitOfWorkSQLAlchemy
from app.system.exceptions import DbObjectCannotBeCreatedError

pytestmark = pytest.mark.asyncio


class TestUnitOfWorkSQLAlchemy:
    async def test_uow_user(self) -> None:
        uow = UnitOfWorkSQLAlchemy(RepositoryUserSQL)
        async with uow:
            assert uow.db.is_active
            assert uow.repository

    async def test_uow_commit(self, user_domain: DomainUser) -> None:
        uow = UnitOfWorkSQLAlchemy(RepositoryUserSQL)
        # Raise error if user with specific email already exists
        async with uow:
            uow.db.add(user_domain)
            await uow.commit()
            uow.db.bind.engine.dispose()

    async def test_uow_rollback(self, user_domain: DomainUser) -> None:
        uow = UnitOfWorkSQLAlchemy(RepositoryUserSQL)
        # Raise error if user with specific email already exists
        async with uow:
            uow.db.add(user_domain)
            await uow.rollback()
        assert len(uow.db.new) == 0

    async def test_raise_error_db_record_duplicate(self, user_domain: DomainUser) -> None:
        uow = UnitOfWorkSQLAlchemy(RepositoryUserSQL)
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
            uow.db.bind.engine.dispose()
