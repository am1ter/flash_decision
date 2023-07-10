from __future__ import annotations

import contextlib
from asyncio import TaskGroup
from typing import TYPE_CHECKING, Self, cast

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.bootstrap import Bootstrap
from app.infrastructure.units_of_work.base import UnitOfWork
from app.system.exceptions import DbObjectCannotBeCreatedError

if TYPE_CHECKING:
    from app.infrastructure.repositories.base import RepositorySQLAlchemy


class UnitOfWorkSQLAlchemy(UnitOfWork):
    """
    Implementation of the `UnitOfWork` pattern using SQLAlchemy engine.
    Also it supports creating internal `TaskGroup` for scheduling async tasks.
    """

    def __init__(
        self,
        repository_type: type[RepositorySQLAlchemy],
        db_factory: sessionmaker = Bootstrap().db_session_factory,
        create_task_group: bool | None = None,
    ) -> None:
        self._db_factory = db_factory
        self._repository_type = repository_type
        self._create_task_group = create_task_group

    async def __aenter__(self) -> Self:
        self.db = cast(AsyncSession, self._db_factory())
        self.repository = self._repository_type(self.db)
        if self._create_task_group:
            self.task_group = TaskGroup()
            await self.task_group.__aenter__()
        return await super().__aenter__()

    async def __aexit__(self, *args) -> None:
        with contextlib.suppress(AttributeError):
            await self.task_group.__aexit__(*args)
        await super().__aexit__(*args)
        await self.db.close()

    async def commit(self) -> None:
        try:
            await self.db.commit()
        except IntegrityError as e:
            raise DbObjectCannotBeCreatedError from e

    async def rollback(self) -> None:
        self.db.expunge_all()
        await self.db.rollback()
        pass

    def __call__(self) -> Self:
        return self
