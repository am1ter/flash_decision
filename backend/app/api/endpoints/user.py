from attrs import asdict
from fastapi import APIRouter, Request

from app.api.schemas.base import Resp
from app.api.schemas.user import ReqSignIn, ReqSignUp, ReqSystemInfo, RespSignIn, RespSignUp
from app.services.user import ServiceUserDep

router = APIRouter(prefix="/api/v1/user")


def parse_request_system_info(raw_request: Request) -> ReqSystemInfo:
    """Extract system info from request"""
    assert raw_request.client, "Wrong request"
    req_system_info = ReqSystemInfo(
        ip_address=raw_request.client.host, user_agent=raw_request.headers["User-Agent"]
    )
    return req_system_info


@router.post("/sign-up", response_model=Resp)
async def sign_up(payload: ReqSignUp, raw_request: Request, service_user: ServiceUserDep) -> Resp:
    """Create new user and record it to db"""

    req_system_info = parse_request_system_info(raw_request)
    new_user = await service_user.sign_up(req=payload, req_system_info=req_system_info)

    data = RespSignUp(**asdict(new_user, recurse=False), token="")
    return Resp(data=data)


@router.post("/sign-in", response_model=Resp)
async def sign_in(payload: ReqSignIn, raw_request: Request, service_user: ServiceUserDep) -> Resp:
    """Create new user and record it to db"""

    req_system_info = parse_request_system_info(raw_request)
    new_user = await service_user.sign_in(req=payload, req_system_info=req_system_info)

    data = RespSignIn(**asdict(new_user, recurse=False), token="")
    return Resp(data=data)
