from abc import ABCMeta, abstractmethod
from typing import Any


class Db(metaclass=ABCMeta):
    """ABC class for describing all databases"""

    def __init__(self) -> None:
        self.engine = self.get_engine()

    @abstractmethod
    def get_engine(self) -> Any:
        """Configure database connection parameters and create a connecter"""

    @abstractmethod
    async def healthcheck(self) -> bool:
        """Run self check"""
