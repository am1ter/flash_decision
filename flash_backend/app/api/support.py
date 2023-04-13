from fastapi import APIRouter

from app.schemas.base import Resp
from app.schemas.support import RespDataHealthcheck


router = APIRouter(prefix="/api/v1/support")


@router.get("/healthcheck", response_model=Resp)
async def make_healthcheck() -> Resp:
    """Check system coditions"""
    data = RespDataHealthcheck(isAppUp=True)
    return Resp(data=data)
