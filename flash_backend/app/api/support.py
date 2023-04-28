from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas.base import Resp
from app.schemas.support import RespDataHealthcheck

router = APIRouter(prefix="/api/v1/support")


@router.get("/healthcheck", response_model=Resp)
async def make_healthcheck(session: AsyncSession = Depends(get_session)) -> Resp:
    """Check system coditions"""

    # Always true
    is_app_up = True

    # Try to connect to db
    async with session as conn:
        try:
            await conn.execute(text("SELECT 1"))
            is_db_up = True
        except Exception:  # noqa: BLE001
            is_db_up = False

    # Response
    data = RespDataHealthcheck(is_app_up=is_app_up, is_db_up=is_db_up)
    return Resp(data=data)
