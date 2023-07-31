from asyncio import TaskGroup
from contextlib import suppress
from typing import Any, Protocol

import structlog
from attrs import asdict

from app.bootstrap import Bootstrap
from app.domain.support import Healthcheck

# Create logger
logger = structlog.get_logger()


class HasHealthcheck(Protocol):
    async def healthcheck(self) -> bool:
        ...


class HasResult(Protocol):
    def result(self) -> Any:
        ...


class ServiceSupport:
    """Service for system self check"""

    async def healthcheck(self) -> Healthcheck:
        """Create async tasks to run healthcheck for all external services"""

        class NoneResult(HasResult):
            def result(self) -> bool:
                """Emulate behaviour of the TaskGroup's task"""
                return False

        healthchecks: dict[HasHealthcheck, HasResult] = {
            Bootstrap().db_sql: NoneResult(),
            Bootstrap().db_nosql: NoneResult(),
            Bootstrap().cache: NoneResult(),
            Bootstrap().provider_stocks: NoneResult(),
            Bootstrap().provider_crypto: NoneResult(),
        }
        async with TaskGroup() as tg:
            for service in healthchecks:
                with suppress(AttributeError):
                    healthchecks[service] = tg.create_task(service.healthcheck())
        result = Healthcheck(
            is_app_up=True,
            is_sql_up=healthchecks[Bootstrap().db_sql].result(),
            is_nosql_up=healthchecks[Bootstrap().db_nosql].result(),
            is_cache_up=healthchecks[Bootstrap().cache].result(),
            is_provider_stocks_up=healthchecks[Bootstrap().provider_stocks].result(),
            is_provider_crypto_up=healthchecks[Bootstrap().provider_crypto].result(),
        )
        if all(asdict(result).values()):
            await logger.ainfo_finish(cls=self.__class__, show_func_name=True, result=result)
        else:
            await logger.aerror_finish(cls=self.__class__, show_func_name=True, result=result)
        return result
