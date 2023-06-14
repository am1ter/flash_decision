from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.bootstrap import Bootstrap

if TYPE_CHECKING:
    from app.infrastructure.repositories.base import RepositorySQLAlchemy


class UnitOfWork(ABC):
    """
    Maintains a list of objects affected by a business transaction.
    https://martinfowler.com/eaaCatalog/unitOfWork.html
    """

    async def __aenter__(self) -> UnitOfWork:
        return self

    async def __aexit__(self, *args) -> None:
        await self.rollback()

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass


class UnitOfWorkSQLAlchemy(UnitOfWork):
    """Implementation of the `UnitOfWork` pattern using SQLAlchemy engine"""

    def __init__(
        self,
        repository_type: type[RepositorySQLAlchemy],
        db_factory: sessionmaker = Bootstrap().db_session_factory,
    ) -> None:
        self._db_factory = db_factory
        self._repository_type = repository_type

    async def __aenter__(self) -> UnitOfWork:
        self.db = cast(AsyncSession, self._db_factory())
        self.repository = self._repository_type(self.db)
        return await super().__aenter__()

    async def __aexit__(self, *args) -> None:
        await super().__aexit__(*args)
        await self.db.close()

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        self.db.expunge_all()
        await self.db.rollback()
        pass

    def __call__(self) -> UnitOfWorkSQLAlchemy:
        return self
