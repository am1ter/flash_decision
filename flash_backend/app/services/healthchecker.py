from sqlalchemy import text

from app.db import get_connection


class Healthchecker:
    """Service for system self check"""

    async def check_db_connection(self) -> bool:
        async with get_connection() as conn:
            try:
                await conn.execute(text("SELECT 1"))
            except Exception:  # noqa: BLE001
                check_result = False
            else:
                check_result = True
        return check_result
