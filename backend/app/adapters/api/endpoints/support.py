from attrs import asdict
from fastapi import APIRouter

from app.adapters.api.dependencies.dependencies import ServiceSupportDep
from app.adapters.api.schemas.base import Resp, RespMeta
from app.adapters.api.schemas.support import RespDataHealthcheck
from app.system.config import Settings

router = APIRouter(prefix=f"/{Settings().general.BACKEND_API_PREFIX}/support")


@router.get("/healthcheck")
async def run_healthcheck(service: ServiceSupportDep) -> Resp[RespMeta, RespDataHealthcheck]:
    """Run system self check"""
    result = await service.healthcheck()
    data = RespDataHealthcheck(**asdict(result))
    return Resp(data=data)
