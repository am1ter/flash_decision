from abc import ABCMeta
from collections.abc import Callable

from attrs import define

from app.domain.interfaces.unit_of_work import UnitOfWork


@define(kw_only=False, slots=False, hash=True)
class Service(metaclass=ABCMeta):
    """Abstract class that defines Interface for all Service layer classes"""

    uow: UnitOfWork

    def __call__(self) -> Callable:
        """Create new class instance"""
        return self.__class__(self.uow)
