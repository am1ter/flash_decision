from contextlib import suppress

import pytest

from app.bootstrap import Bootstrap
from app.infrastructure.cache.redis import CacheRedis


@pytest.fixture()
def redis() -> CacheRedis:
    with suppress(KeyError):
        type(Bootstrap)._instances.pop(CacheRedis)
    return CacheRedis()


@pytest.fixture()
def mock_cache_record() -> dict:
    return {"dict_key": ["list_item_1", "list_item_2"]}


@pytest.fixture()
def mock_cache_multi_records(mock_cache_record: dict) -> dict:
    return {"mock_cache_record_1": mock_cache_record, "mock_cache_record_2": mock_cache_record}


class TestCacheRedis:
    @pytest.mark.dependency()
    @pytest.mark.asyncio()
    async def test_set(self, redis: CacheRedis, mock_cache_record: dict) -> None:
        await redis.set("mock_cache_record", mock_cache_record)
        rec = await redis.redis.json().get("mock_cache_record")
        assert rec == mock_cache_record
        expire_time = await redis.redis.pttl("mock_cache_record")
        assert expire_time > 0

    @pytest.mark.dependency(depends=["TestCacheRedis::test_set"])
    @pytest.mark.asyncio()
    async def test_get(self, redis: CacheRedis, mock_cache_record: dict) -> None:
        rec = await redis.get("mock_cache_record")
        assert rec == mock_cache_record

    @pytest.mark.dependency()
    @pytest.mark.asyncio()
    async def test_mset(self, redis: CacheRedis, mock_cache_multi_records: dict) -> None:
        await redis.mset(mock_cache_multi_records)
        recs = await redis.redis.json().mget(list(mock_cache_multi_records.keys()), ".")
        assert recs == list(mock_cache_multi_records.values())
        expire_time_1 = await redis.redis.pttl(list(mock_cache_multi_records.keys())[0])
        expire_time_2 = await redis.redis.pttl(list(mock_cache_multi_records.keys())[1])
        assert expire_time_1 > 0 and expire_time_2 > 0

    @pytest.mark.dependency(depends=["TestCacheRedis::test_mset"])
    @pytest.mark.asyncio()
    async def test_mget(self, redis: CacheRedis, mock_cache_multi_records: dict) -> None:
        recs = await redis.mget(list(mock_cache_multi_records.keys()))
        assert recs == list(mock_cache_multi_records.values())

    @pytest.mark.asyncio()
    async def test_healthcheck(self, redis: CacheRedis) -> None:
        result = await redis.healthcheck()
        assert result is True
