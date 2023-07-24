from abc import ABC, abstractmethod
from typing import Self


class UnitOfWork(ABC):
    """
    Maintains a list of objects affected by a business transaction.
    https://martinfowler.com/eaaCatalog/unitOfWork.html
    """

    @abstractmethod
    async def __aenter__(self) -> Self:
        pass

    @abstractmethod
    async def __aexit__(self, *args) -> None:
        pass
