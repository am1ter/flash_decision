from typing import Annotated

from attrs import asdict
from fastapi import APIRouter, Depends
from uuid6 import UUID

from app.api.schemas.base import Resp, RespMeta
from app.api.schemas.session import ReqSession, RespSession, RespSessionOptions
from app.domain.base import custom_serializer
from app.domain.session import DomainSession
from app.services.session import ServiceSession, SessionParams
from app.services.session_iteration import ServiceIteration
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
    req_session: ReqSession | None = None,
) -> Resp[RespMeta, RespSession]:
    """Start new session: receive session's mode and options, download quotes, create iterations"""
    assert auth.user
    session_params = SessionParams(**req_session.dict()) if req_session else None
    session_quotes = await service_session.create_session(mode, session_params, auth.user)
    await service_iteration.create_iterations(session_quotes)
    data = _resp_session_by_session(session_quotes.session)
    return Resp(data=data)


@router.get("/")
async def get_session_info(
    session_id: str,
    service_session: ServiceSessionDep,
    auth: ServiceAuthorizationDep,
) -> Resp[RespMeta, RespSession]:
    """Extract session from db and send it to the client"""
    session = await service_session.get_session(UUID(session_id))
    data = _resp_session_by_session(session)
    return Resp(data=data)


def _resp_session_by_session(session: DomainSession) -> RespSession:
    return RespSession(
        _id=str(session._id),
        mode=session.mode.value,
        ticker_type=session.ticker.ticker_type.value,
        ticker_symbol=session.ticker.symbol,
        timeframe=session.timeframe.value,
        barsnumber=session.barsnumber.value,
        timelimit=session.timelimit.value,
        iterations=session.iterations.value,
        slippage=session.slippage.value,
        fixingbar=session.fixingbar.value,
        status=session.status.value,
    )
