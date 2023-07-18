from __future__ import annotations

from typing import TYPE_CHECKING, Self, cast

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.bootstrap import Bootstrap
from app.infrastructure.units_of_work.base import UnitOfWork
from app.system.exceptions import DbConnectionError, DbObjectCannotBeCreatedError

if TYPE_CHECKING:
    from app.infrastructure.repositories.base import RepositorySQLAlchemy


class UnitOfWorkSQLAlchemy(UnitOfWork):
    """Implementation of the `UnitOfWork` pattern using SQLAlchemy engine"""

    def __init__(
        self,
        repository_type: type[RepositorySQLAlchemy],
        db_factory: sessionmaker = Bootstrap().sql_session_factory,
    ) -> None:
        self._db_factory = db_factory
        self._repository_type = repository_type

    async def __aenter__(self) -> Self:
        self._db = cast(AsyncSession, self._db_factory())
        self.repository = self._repository_type(self._db)
        return await super().__aenter__()

    async def __aexit__(self, *args) -> None:
        await super().__aexit__(*args)
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
