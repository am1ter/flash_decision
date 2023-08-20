from abc import ABCMeta, abstractmethod
from typing import Generic, Self, TypeVar

from app.domain.interfaces.db import Db
from app.domain.interfaces.repository import Repository

RepositoryType = TypeVar("RepositoryType", bound=Repository)


class UnitOfWork(Generic[RepositoryType], metaclass=ABCMeta):
    """
    Maintains a list of objects affected by a business transaction.
    https://martinfowler.com/eaaCatalog/unitOfWork.html
    """

    db_factory: Db
    repository: RepositoryType

    @abstractmethod
    async def __aenter__(self) -> Self:
        pass

    @abstractmethod
    async def __aexit__(self, *args) -> None:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass
