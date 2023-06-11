from collections.abc import Callable
from contextlib import _AsyncGeneratorContextManager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.bootstrap import bootstrap
from app.system.logger import logger

DbConnectionFactory = Callable[..., _AsyncGeneratorContextManager[AsyncConnection]]


class ServiceSupport:
    """Service for system self check"""

    def __init__(self, db_conn_factory: DbConnectionFactory = bootstrap.db_conn_factory) -> None:
        self.db_conn_factory = db_conn_factory

    async def check_db_connection(self) -> bool:
        try:
            async with self.db_conn_factory() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception:  # noqa: BLE001
            check_result = False
        else:
            check_result = True

        logger.info_finish(cls=self.__class__, show_func_name=True, result=check_result)
        return check_result
