from attrs import asdict
from fastapi import APIRouter

from app.api.schemas.base import Resp
from app.api.schemas.user import ReqSignUp, RespSignUp
from app.services.user import ServiceUserDep

router = APIRouter(prefix="/api/v1/user")


@router.post("/sign-up", response_model=Resp)
async def test(payload: ReqSignUp, service_user: ServiceUserDep) -> Resp:
    """Create new user and record it to db"""

    await service_user.create_user(payload)
    new_user = await service_user.get_user_by_request(payload)

    data = RespSignUp(**asdict(new_user), token="")
    return Resp(data=data)
