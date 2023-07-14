from asyncio import TaskGroup

from attrs import asdict
from sqlalchemy import text

from app.bootstrap import Bootstrap
from app.domain.support import HealthCheck
from app.system.logger import create_logger

# Create logger
logger = create_logger("backend.service.support")


class ServiceSupport:
    """Service for system self check"""

    async def _check_db_connection(self) -> bool:
        try:
            async with Bootstrap().db_conn_factory() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception:  # noqa: BLE001
            check_result = False
        else:
            check_result = True

        return check_result

    async def healthcheck(self) -> HealthCheck:
        async with TaskGroup() as tg:
            is_db_up = tg.create_task(self._check_db_connection())
            is_cache_up = tg.create_task(Bootstrap().cache.healthcheck())
            is_provider_stocks_up = tg.create_task(Bootstrap().provider_stocks.healthcheck())
            is_provider_crypto_up = tg.create_task(Bootstrap().provider_crypto.healthcheck())
        result = HealthCheck(
            is_app_up=True,
            is_db_up=is_db_up.result(),
            is_cache_up=is_cache_up.result(),
            is_provider_stocks_up=is_provider_stocks_up.result(),
            is_provider_crypto_up=is_provider_crypto_up.result(),
        )
        if all(asdict(result).values()):
            await logger.ainfo_finish(cls=self.__class__, show_func_name=True, result=result)
        else:
            await logger.aerror(
                "Operation completed with errors",
                cls=self.__class__.__name__,
                func="healthcheck",
                result=result,
            )
        return result
