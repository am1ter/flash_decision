from uuid import UUID

from fastapi import APIRouter

from app.adapters.api.dependencies.dependencies import (
    ServiceAuthorizationDep,
    ServiceIterationDep,
    ServiceSessionDep,
)
from app.adapters.api.schemas.session_iteration import RespIteration
from app.system.config import Settings

router = APIRouter(prefix=f"/{Settings().general.BACKEND_API_PREFIX}/iteration")


@router.get("/", status_code=200)
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
