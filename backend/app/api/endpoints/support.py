from fastapi import APIRouter

from app.api.schemas.base import Resp
from app.api.schemas.support import RespDataHealthcheck
from app.services.support import ServiceSupportDep

router = APIRouter(prefix="/api/v1/support")


@router.get("/healthcheck", response_model=Resp)
async def run_healthcheck(service_support: ServiceSupportDep) -> Resp:
    """Run system self check"""

    is_app_up = True
    is_db_up = await service_support.check_db_connection()

    data = RespDataHealthcheck(is_app_up=is_app_up, is_db_up=is_db_up)
    return Resp(data=data)
