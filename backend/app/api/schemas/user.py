from pydantic import BaseModel, Extra, Field

from app.api.schemas.base import ReqMeta, RespData
from app.system.constants import UserStatus


class ReqSystemInfo(BaseModel):
    ip_address: str
    user_agent: str


class BaseSign(BaseModel):
    class Config:
        """Disable Extra.allow which is inherited from meta classes"""

        extra = Extra.ignore


class ReqSignUp(BaseSign, ReqMeta):
    email: str
    name: str
    password: str = Field(repr=False)


class RespSignUp(BaseSign, RespData):
    id: int
    email: str
    status: UserStatus
    token: str


class ReqSignIn(BaseSign, ReqMeta):
    email: str
    password: str = Field(repr=False)


class RespSignIn(BaseSign, ReqMeta):
    email: str
    status: UserStatus
    token: str
