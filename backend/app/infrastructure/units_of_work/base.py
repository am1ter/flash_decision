from __future__ import annotations

from abc import ABC, abstractmethod


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
