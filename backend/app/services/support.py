from collections.abc import Callable
from contextlib import _AsyncGeneratorContextManager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.bootstrap import Bootstrap
from app.system.logger import logger

DbConnFactory = Callable[..., _AsyncGeneratorContextManager[AsyncConnection]]


class ServiceSupport:
    """Service for system self check"""

    def __init__(self, db_conn_factory: DbConnFactory = Bootstrap().db_conn_factory) -> None:
        self.db_conn_factory = db_conn_factory

    async def check_db_connection(self) -> bool:
        try:
            async with self.db_conn_factory() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception:  # noqa: BLE001
            check_result = False
        else:
            check_result = True

        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, result=check_result)
        return check_result
