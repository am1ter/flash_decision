from fastapi import APIRouter

from app.schemas.base import Resp
from app.schemas.support import RespDataHealthcheck

router = APIRouter(prefix="/api/v1/support")


@router.get("/healthcheck", response_model=Resp)
async def make_healthcheck() -> Resp:
    """Check system coditions"""
    is_app_up = True
    is_db_up = True
    data = RespDataHealthcheck(is_app_up=is_app_up, is_db_up=is_db_up)
    return Resp(data=data)
