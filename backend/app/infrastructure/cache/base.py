from abc import ABCMeta, abstractmethod
from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal
from typing import TypeAlias

JSON: TypeAlias = Mapping[str, "JSON"] | Sequence["JSON"] | str | int | Decimal | bool | None


class Cache(metaclass=ABCMeta):
    @abstractmethod
    async def get(self, key: str) -> JSON:
        """Retrieve a single JSON (dict) from the cache based on the key"""

    @abstractmethod
    async def mget(self, keys: Iterable[str]) -> list[JSON]:
        """Retrieve multiple JSONs (dicts) from the cache based on the given keys"""

    @abstractmethod
    async def set(self, key: str, value: JSON) -> None:
        """Store a single JSON (dict) in the cache with the specified key"""

    @abstractmethod
    async def mset(self, mapping: Mapping[str, JSON]) -> None:
        """Store multiple JSONs (dicts) in the cache based on the provided key-value mapping"""

    @abstractmethod
    async def healthcheck(self) -> bool:
        """Check if cache is available"""
