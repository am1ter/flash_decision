from __future__ import annotations

from typing import TYPE_CHECKING, Self

from sqlalchemy.exc import IntegrityError

from app.bootstrap import Bootstrap
from app.domain.unit_of_work import UnitOfWork
from app.system.exceptions import DbConnectionError, DbObjectCannotBeCreatedError

if TYPE_CHECKING:
    from app.infrastructure.databases.sql import DbSql
    from app.infrastructure.repositories.base import RepositorySqlAlchemy


class UnitOfWorkSqlAlchemy(UnitOfWork):
    """Implementation of the `UnitOfWork` pattern using SQLAlchemy engine"""

    def __init__(
        self,
        repository_type: type[RepositorySqlAlchemy],
        db_factory: DbSql = Bootstrap().db_sql,
    ) -> None:
        self._repository_type = repository_type
        self._db_factory = db_factory

    async def __aenter__(self) -> Self:
        session = self._db_factory.get_session()
        self._db = await session.__aenter__()
        self.repository = self._repository_type(self._db)
        return self

    async def __aexit__(self, *args) -> None:
        await self.rollback()
        await self._db.close()

    async def commit(self) -> None:
        try:
            await self._db.commit()
        except IntegrityError as e:
            raise DbObjectCannotBeCreatedError from e
        except ConnectionRefusedError as e:
            raise DbConnectionError from e

    async def rollback(self) -> None:
        self._db.expunge_all()
        await self._db.rollback()
        pass

    def __call__(self) -> Self:
        return self
