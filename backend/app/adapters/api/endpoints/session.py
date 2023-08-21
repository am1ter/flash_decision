from uuid import UUID

from attrs import asdict
from fastapi import APIRouter

from app.adapters.api.dependencies.dependencies import (
    ServiceAuthorizationDep,
    ServiceIterationDep,
    ServiceSessionDep,
)
from app.adapters.api.schemas.base import Resp, RespMeta
from app.adapters.api.schemas.session import (
    ReqSession,
    RespSession,
    RespSessionInfo,
    RespSessionOptions,
    RespSessionResult,
)
from app.domain.interfaces.domain import custom_serializer
from app.domain.session import Session
from app.services.session import SessionParams
from app.system.config import Settings
from app.system.constants import SessionMode

router = APIRouter(prefix=f"/{Settings().general.BACKEND_API_PREFIX}/session")


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
) -> Resp[RespMeta, RespSessionInfo]:
    """Start new session: receive session's mode and options, download quotes, create iterations"""
    assert auth.user
    session_params = SessionParams(**req_session.dict()) if req_session else None
    session_quotes = await service_session.create_session(mode, session_params, auth.user)
    await service_iteration.create_iterations(session_quotes)
    data = _resp_session_by_session(session_quotes.session)
    return Resp(data=data)


@router.get("/")
async def get_session_info(
    *,
    session_id: UUID,
    info: bool = False,
    result: bool = False,
    service_session: ServiceSessionDep,
    auth: ServiceAuthorizationDep,
) -> Resp[RespMeta, RespSession]:
    """Extract session info and/or session results from db and send it to the client"""
    assert auth.user
    session = await service_session.get_session(session_id=session_id, user=auth.user)
    resp_info = _resp_session_by_session(session) if info else None
    if result:
        session_result = await service_session.calc_session_result(session)
        resp_res = RespSessionResult(**asdict(session_result, value_serializer=custom_serializer))
    else:
        resp_res = None
    data = RespSession(info=resp_info, result=resp_res)
    return Resp(data=data)


def _resp_session_by_session(session: Session) -> RespSessionInfo:
    return RespSessionInfo(
        session_id=session._id,
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
