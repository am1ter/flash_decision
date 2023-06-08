from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas.base import Resp, RespMeta
from app.api.schemas.support import RespDataHealthcheck
from app.services.support import ServiceSupport

router = APIRouter(prefix="/api/v1/support")

# Internal dependencies
ServiceSupportDep = Annotated[ServiceSupport, Depends()]


@router.get("/healthcheck")
async def run_healthcheck(service: ServiceSupportDep) -> Resp[RespMeta, RespDataHealthcheck]:
    """Run system self check"""

    is_app_up = True
    is_db_up = await service.check_db_connection()

    data = RespDataHealthcheck(is_app_up=is_app_up, is_db_up=is_db_up)
    return Resp(data=data)
