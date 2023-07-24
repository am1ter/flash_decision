from typing import Annotated

from attrs import asdict
from fastapi import APIRouter, Depends

from app.api.schemas.base import Resp, RespMeta
from app.api.schemas.session import ReqSession, RespSession, RespSessionOptions
from app.domain.base import custom_serializer
from app.services.iteration import ServiceIteration
from app.services.session import ServiceSession
from app.services.user_authorization import ServiceAuthorization, verify_authorization
from app.system.config import Settings
from app.system.constants import SessionMode

router = APIRouter(prefix=f"/{Settings().general.BACKEND_API_PREFIX}/session")

# Internal dependencies
ServiceSessionDep = Annotated[ServiceSession, Depends()]
ServiceIterationDep = Annotated[ServiceIteration, Depends()]
ServiceAuthorizationDep = Annotated[ServiceAuthorization, Depends(verify_authorization)]


@router.get("/options")
async def collect_session_options(
    service: ServiceSessionDep, auth: ServiceAuthorizationDep
) -> Resp[RespMeta, RespSessionOptions]:
    """Send lists of all available parameters (options) for the form `Create new session`"""
    options = await service.collect_session_options()
    meta = RespMeta(tickers_count=len(options.all_ticker))
    data = RespSessionOptions(**asdict(options, value_serializer=custom_serializer))
    return Resp(meta=meta, data=data)


@router.post("/{mode}")
async def start_new_session(
    mode: SessionMode,
    service_session: ServiceSessionDep,
    service_iteration: ServiceIterationDep,
    auth: ServiceAuthorizationDep,
    session_params: ReqSession | None = None,
) -> Resp[RespMeta, RespSession]:
    """Start new session: receive session's mode and options, download quotes, create iterations"""
    assert auth.user
    session = await service_session.create_session(mode, session_params, auth.user)
    await service_iteration.create_iterations(session)
    meta = RespMeta()
    data = RespSession(_id=session._id)
    return Resp(meta=meta, data=data)
