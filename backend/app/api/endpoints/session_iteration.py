from typing import Annotated

from fastapi import APIRouter, Depends
from uuid6 import UUID

from app.api.schemas.session_iteration import RespIteration
from app.services.session_iteration import ServiceIteration
from app.services.user_authorization import ServiceAuthorization, verify_authorization
from app.system.config import Settings

router = APIRouter(prefix=f"/{Settings().general.BACKEND_API_PREFIX}/iteration")

# Internal dependencies
ServiceIterationDep = Annotated[ServiceIteration, Depends()]
ServiceAuthorizationDep = Annotated[ServiceAuthorization, Depends(verify_authorization)]


@router.get("/")
async def render_chart(
    session_id: str, iteration_num: int, service_iteration: ServiceIterationDep
) -> RespIteration:
    chart = await service_iteration.render_chart(UUID(session_id), iteration_num)
    return RespIteration(chart=chart)
