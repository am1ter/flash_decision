from __future__ import annotations

from threading import Lock
from typing import Generic, TypeVar

SingletonInstance = TypeVar("SingletonInstance")


class SingletonMeta(type, Generic[SingletonInstance]):
    """
    Thread-safe implementation of Singleton pattern.
    https://python-patterns.guide/gang-of-four/singleton/
    """

    _instances: dict[SingletonMeta[SingletonInstance], SingletonInstance] = {}
    _lock: Lock = Lock()

    def __call__(cls: SingletonMeta[SingletonInstance], *args, **kwargs) -> SingletonInstance:
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
