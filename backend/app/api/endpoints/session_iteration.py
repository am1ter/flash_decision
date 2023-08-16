from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.schemas.session_iteration import RespIteration
from app.services.session import ServiceSession
from app.services.session_iteration import ServiceIteration
from app.services.user_authorization import ServiceAuthorization, verify_authorization
from app.system.config import Settings

router = APIRouter(prefix=f"/{Settings().general.BACKEND_API_PREFIX}/iteration")

# Internal dependencies
ServiceSessionDep = Annotated[ServiceSession, Depends()]
ServiceIterationDep = Annotated[ServiceIteration, Depends()]
ServiceAuthorizationDep = Annotated[ServiceAuthorization, Depends(verify_authorization)]


@router.get("/")
async def get_next_iteration(
    session_id: str,
    service_session: ServiceSessionDep,
    service_iteration: ServiceIterationDep,
    auth: ServiceAuthorizationDep,
) -> RespIteration:
    assert auth.user
    session = await service_session.get_session(session_id=UUID(session_id), user=auth.user)
    iteration = await service_iteration.get_next_iteration(session)
    return RespIteration(iteration_num=iteration.iteration_num, chart=iteration.chart)
