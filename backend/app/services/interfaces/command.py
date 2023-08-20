from abc import ABCMeta, abstractmethod
from typing import Any


class Command(metaclass=ABCMeta):
    @abstractmethod
    def execute(self) -> Any:
        pass
