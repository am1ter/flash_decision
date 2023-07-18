from __future__ import annotations

from threading import Lock
from typing import Generic, TypeVar

SingletonInstance = TypeVar("SingletonInstance")


class SingletonMeta(type, Generic[SingletonInstance]):
    """
    Thread-safe implementation of Singleton pattern.
    https://python-patterns.guide/gang-of-four/singleton/
    """

    _instances: dict[SingletonMeta[SingletonInstance], SingletonInstance] = {}  # noqa: RUF012
    _locks: dict[SingletonMeta[SingletonInstance], Lock] = {}  # noqa: RUF012

    def __call__(cls: SingletonMeta[SingletonInstance], *args, **kwargs) -> SingletonInstance:
        if cls not in cls._instances:
            cls._locks[cls] = Lock()
            with cls._locks[cls]:
                instance = super().__call__(*args, **kwargs)
                if cls not in cls._instances:
                    cls._instances[cls] = instance
        return cls._instances[cls]
