from typing import Annotated

from attrs import asdict
from fastapi import APIRouter, Depends

from app.api.schemas.base import Resp, RespMeta
from app.api.schemas.support import RespDataHealthcheck
from app.services.support import ServiceSupport
from app.system.config import settings

router = APIRouter(prefix=f"/{settings.BACKEND_API_PREFIX}/support")

# Internal dependencies
ServiceSupportDep = Annotated[ServiceSupport, Depends()]


@router.get("/healthcheck")
async def run_healthcheck(service: ServiceSupportDep) -> Resp[RespMeta, RespDataHealthcheck]:
    """Run system self check"""
    result = await service.healthcheck()
    data = RespDataHealthcheck(**asdict(result))
    return Resp(data=data)
