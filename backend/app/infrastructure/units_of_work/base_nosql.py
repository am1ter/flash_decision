from typing import Self

from app.bootstrap import Bootstrap
from app.infrastructure.nosql import DbNoSql
from app.infrastructure.repositories.base import RepositoryNoSqlMongo
from app.infrastructure.units_of_work.base import UnitOfWork


class UnitOfWorkNoSqlMongo(UnitOfWork):
    """Implementation of the `UnitOfWork` pattern using Mongo database"""

    def __init__(
        self,
        repository_type: type[RepositoryNoSqlMongo],
        db_factory: DbNoSql = Bootstrap().db_nosql,
    ) -> None:
        self._repository_type = repository_type
        self._db_factory = db_factory

    async def __aenter__(self) -> Self:
        self.repository = self._repository_type(self._db_factory)
        return self

    async def __aexit__(self, *args) -> None:
        pass

    def __call__(self) -> Self:
        return self
