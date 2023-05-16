from pydantic import BaseModel, Extra, Field

from app.api.schemas.base import ReqMeta, RespData
from app.system.constants import UserStatus


class ReqSystemInfo(BaseModel):
    ip_address: str
    user_agent: str


class BaseSign(BaseModel):
    email: str

    class Config:
        """Disable Extra.allow which is inherited from meta classes"""

        extra = Extra.ignore


class ReqSignUp(BaseSign, ReqMeta):
    name: str
    password: str = Field(repr=False)


class RespSignUp(BaseSign, RespData):
    id: int
    status: UserStatus
    token: str


class ReqSignIn(BaseSign, ReqMeta):
    password: str = Field(repr=False)


class RespSignIn(BaseSign, ReqMeta):
    status: UserStatus
    token: str
