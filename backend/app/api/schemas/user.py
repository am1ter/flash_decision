from pydantic import BaseModel, Field

from app.api.schemas.base import RespData


class ReqSystemInfo(BaseModel):
    ip_address: str
    user_agent: str


class ReqSignUp(BaseModel):
    email: str
    name: str
    password: str = Field(repr=False)


class RespSignUp(RespData):
    id: str
    email: str
    status: str
    access_token: str
    token_type: str = "bearer"


class ReqSignIn(BaseModel):
    username: str  # Email, field name `username` is the requirement of OAuth2 specification
    password: str = Field(repr=False)
    # To comply with OAuth2 protocol
    scope: str | None = None
    grant_type: str = "password"


class RespSignIn(RespData):
    id: str
    email: str
    status: str
    access_token: str
    token_type: str = "bearer"
