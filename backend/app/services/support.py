from asyncio import TaskGroup

import structlog
from attrs import asdict
from sqlalchemy import text

from app.bootstrap import Bootstrap
from app.domain.support import HealthCheck

# Create logger
logger = structlog.get_logger()


class ServiceSupport:
    """Service for system self check"""

    async def _check_sql_connection(self) -> bool:
        try:
            async with Bootstrap().db_sql.get_connection() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception:  # noqa: BLE001
            check_result = False
        else:
            check_result = True

        return check_result

    async def healthcheck(self) -> HealthCheck:
        async with TaskGroup() as tg:
            is_sql_up = tg.create_task(self._check_sql_connection())
            is_cache_up = tg.create_task(Bootstrap().cache.healthcheck())
            is_provider_stocks_up = tg.create_task(Bootstrap().provider_stocks.healthcheck())
            is_provider_crypto_up = tg.create_task(Bootstrap().provider_crypto.healthcheck())
        result = HealthCheck(
            is_app_up=True,
            is_sql_up=is_sql_up.result(),
            is_cache_up=is_cache_up.result(),
            is_provider_stocks_up=is_provider_stocks_up.result(),
            is_provider_crypto_up=is_provider_crypto_up.result(),
        )
        if all(asdict(result).values()):
            await logger.ainfo_finish(cls=self.__class__, show_func_name=True, result=result)
        else:
            await logger.aerror_finish(cls=self.__class__, show_func_name=True, result=result)
        return result
