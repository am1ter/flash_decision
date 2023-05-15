from attrs import asdict
from fastapi import APIRouter, Request

from app.api.schemas.base import Resp
from app.api.schemas.user import ReqSignUp, ReqSystemInfo, RespSignUp
from app.services.user import ServiceUserDep

router = APIRouter(prefix="/api/v1/user")


@router.post("/sign-up", response_model=Resp)
async def test(payload: ReqSignUp, raw_request: Request, service_user: ServiceUserDep) -> Resp:
    """Create new user and record it to db"""

    # Extract system info from request
    assert raw_request.client, "Wrong request"
    req_system_info = ReqSystemInfo(
        ip_address=raw_request.client.host, user_agent=raw_request.headers["User-Agent"]
    )

    # Business logic
    new_user = await service_user.create_user(req=payload, req_system_info=req_system_info)

    data = RespSignUp(**asdict(new_user, recurse=False), token="")
    return Resp(data=data)
