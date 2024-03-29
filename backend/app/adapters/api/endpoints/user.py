from fastapi import APIRouter, Request

from app.adapters.api.dependencies.dependencies import ServiceUserDep, SignUpFormDep
from app.adapters.api.schemas.user import (
    ReqSignIn,
    ReqSignUp,
    ReqSystemInfo,
    RespSignIn,
    RespSignUp,
)
from app.system.config import Settings

router = APIRouter(prefix=f"/{Settings().general.BACKEND_API_PREFIX}/user")


def parse_request_system_info(raw_request: Request) -> ReqSystemInfo:
    """Extract system info from request"""
    assert raw_request.client, "Wrong request"
    req_system_info = ReqSystemInfo(
        ip_address=raw_request.client.host, user_agent=raw_request.headers["User-Agent"]
    )
    return req_system_info


@router.post("/sign-up", status_code=201)
async def sign_up(
    payload: ReqSignUp, raw_request: Request, service_user: ServiceUserDep
) -> RespSignUp:
    """
    Create new user and record it to the database.
    JWT specification is not compatible with JSON:API specification.
    The app sends response for this endpoint using JWT specification.
    """

    req_system_info = parse_request_system_info(raw_request)
    user = await service_user.sign_up(
        email=payload.email,
        name=payload.name,
        password=payload.password,
        ip_address=req_system_info.ip_address,
        user_agent=req_system_info.user_agent,
    )
    access_token = await service_user.create_access_token(user)

    return RespSignUp(
        id=user._id,
        email=user.email.value,
        status=user.status.value,
        access_token=access_token.access_token,
        token_type=access_token.token_type,
    )


@router.post("/sign-in", status_code=200)
async def sign_in(
    form_data: SignUpFormDep,
    raw_request: Request,
    service_user: ServiceUserDep,
) -> RespSignIn:
    """
    Authenticate user using OAuth2 protocol.
    JWT specification is not compatible with JSON:API specification.
    The app sends response for this endpoint using JWT specification.
    """

    payload = ReqSignIn(username=form_data.username, password=form_data.password)
    req_system_info = parse_request_system_info(raw_request)
    user = await service_user.sign_in(
        username=payload.username,
        password=payload.password,
        ip_address=req_system_info.ip_address,
        user_agent=req_system_info.user_agent,
    )
    access_token = await service_user.create_access_token(user)

    return RespSignIn(
        id=user._id,
        email=user.email.value,
        status=user.status.value,
        access_token=access_token.access_token,
        token_type=access_token.token_type,
    )
