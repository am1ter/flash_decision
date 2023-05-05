from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas.base import Resp
from app.api.schemas.support import RespDataHealthcheck
from app.services.healthchecker import Healthchecker

router = APIRouter(prefix="/api/v1/support")
healthchecker = Annotated[Healthchecker, Depends()]


@router.get("/healthcheck", response_model=Resp)
async def run_healthcheck(healthchecker: healthchecker) -> Resp:
    """Run system self check"""

    is_app_up = True
    is_db_up = await healthchecker.check_db_connection()

    data = RespDataHealthcheck(is_app_up=is_app_up, is_db_up=is_db_up)
    return Resp(data=data)
