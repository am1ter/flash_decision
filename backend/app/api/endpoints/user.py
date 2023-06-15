from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schemas.user import ReqSignIn, ReqSignUp, ReqSystemInfo, RespSignIn, RespSignUp
from app.services.user import ServiceUser
from app.system.config import settings

router = APIRouter(prefix=f"/{settings.BACKEND_API_PREFIX}/user")

# Use FastAPI default tools (dependencies) for OAuth2 authentication
SignUpFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

# Internal dependencies
ServiceUserDep = Annotated[ServiceUser, Depends()]


def parse_request_system_info(raw_request: Request) -> ReqSystemInfo:
    """Extract system info from request"""
    assert raw_request.client, "Wrong request"
    req_system_info = ReqSystemInfo(
        ip_address=raw_request.client.host, user_agent=raw_request.headers["User-Agent"]
    )
    return req_system_info


@router.post("/sign-up")
async def sign_up(
    payload: ReqSignUp, raw_request: Request, service_user: ServiceUserDep
) -> RespSignUp:
    """
    Create new user and record it to the database.
    JWT specification is not compatible with JSON:API specification.
    The app sends response for this endpoint using JWT specification.
    """

    req_system_info = parse_request_system_info(raw_request)
    user = await service_user.sign_up(req=payload, req_system_info=req_system_info)
    access_token = await service_user.create_access_token(user)

    return RespSignUp(
        id=user.id,
        email=user.email.value,
        status=user.status.value,
        access_token=access_token.access_token,
        token_type=access_token.token_type,
    )


@router.post("/sign-in")
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
    user = await service_user.sign_in(req=payload, req_system_info=req_system_info)
    access_token = await service_user.create_access_token(user)

    return RespSignIn(
        id=user.id,
        email=user.email.value,
        status=user.status.value,
        access_token=access_token.access_token,
        token_type=access_token.token_type,
    )
