from collections.abc import Awaitable, Callable, Iterable, Mapping
from functools import wraps
from typing import Any, TypeVar, cast

import structlog
from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from app.domain.cache import JSON, Cache
from app.system.config import Settings
from app.system.exceptions import CacheConnectionError, CacheObjectNotFoundError

# Create logger
logger = structlog.get_logger()

DecoratedFunction = TypeVar("DecoratedFunction", bound=Callable[..., Awaitable])


class CacheRedis(Cache):
    """
    Represents a Cache Protocol implementation that use a REDIS database.
    This class provides methods for retrieving and storing JSON data in a Redis cache.
    It supports only JSON-like objects (python dictionaries).
    Used REDIS's pipelines (transactions) for reducing round-trip time.
    """

    json_path = "."  # Only root-level select/update commands are allowed

    def __init__(self) -> None:
        self.redis: Redis = Redis.from_url(
            Settings().cache.CACHE_REDIS_URL,
            decode_responses=Settings().cache.CACHE_REDIS_DECODE_RESPONSES,
        )

    @staticmethod
    def catch_cache_errors(func: DecoratedFunction) -> DecoratedFunction:
        """Decorator to catch errors during requests to the database"""

        @wraps(func)
        async def inner(*args, **kwargs) -> Any:
            try:
                result = await func(*args, **kwargs)
            except ConnectionError as e:
                await logger.aerror_finish(cls=CacheRedis, show_func_name=True, error=str(e))
                raise CacheConnectionError from e
            return result

        return cast(DecoratedFunction, inner)

    @catch_cache_errors
    async def get(self, key: str) -> JSON:
        value = await self.redis.json().get(key)
        if not value:
            raise CacheObjectNotFoundError
        return value

    @catch_cache_errors
    async def mget(self, keys: Iterable[str]) -> list[JSON]:
        values = await self.redis.json().mget(keys, self.__class__.json_path)
        if not all(values):
            raise CacheObjectNotFoundError
        return values

    @catch_cache_errors
    async def set(self, key: str, value: JSON) -> None:
        async with self.redis.pipeline() as pipe:
            await pipe.json().set(key, self.__class__.json_path, value)
            await pipe.expire(key, Settings().cache.CACHE_TTL)
            await pipe.execute()
        await logger.ainfo("Cache updated", keys=[key])

    @catch_cache_errors
    async def mset(self, mapping: Mapping[str, JSON]) -> None:
        async with self.redis.pipeline() as pipe:
            for k, v in mapping.items():
                pipe.json().set(k, self.__class__.json_path, v)
                pipe.expire(k, Settings().cache.CACHE_TTL)
            await pipe.execute()
        await logger.ainfo("Cache updated", keys=list(mapping.keys()))

    async def healthcheck(self) -> bool:
        try:
            return await self.redis.ping()
        except ConnectionError:
            return False
