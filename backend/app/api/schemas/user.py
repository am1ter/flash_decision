from pydantic import BaseModel, Extra, Field

from app.api.schemas.base import ReqMeta, RespData
from app.system.constants import UserStatus


class ReqSystemInfo(BaseModel):
    ip_address: str
    user_agent: str


class ReqSignUp(ReqMeta):
    email: str
    name: str
    password: str = Field(repr=False)


class RespSignUp(RespData):
    id: int
    email: str
    status: UserStatus
    token: str

    class Config:  # Disable Extra.allow which is inherited from meta class
        extra = Extra.ignore


class ReqSignIn(ReqMeta):
    email: str
    password: str = Field(repr=False)


class RespSignIn(RespData):
    email: str
    status: UserStatus
    token: str

    class Config:  # Disable Extra.allow which is inherited from meta class
        extra = Extra.ignore
