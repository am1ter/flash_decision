from sqlalchemy import text

from app.bootstrap import Bootstrap
from app.system.logger import create_logger

# Create logger
logger = create_logger("backend.service.support")


class ServiceSupport:
    """Service for system self check"""

    async def check_db_connection(self) -> bool:
        try:
            async with Bootstrap().db_conn_factory() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception:  # noqa: BLE001
            check_result = False
        else:
            check_result = True

        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, result=check_result)
        return check_result
