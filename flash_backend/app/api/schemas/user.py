from pydantic import BaseModel, Extra

from app.api.schemas.base import ReqMeta, RespData
from app.system.constants import UserStatus


class ReqSystemInfo(BaseModel):
    ip_address: str
    user_agent: str


class BaseSignUp(BaseModel):
    email: str
    name: str

    class Config:
        """Disable Extra.allow which is inherited from meta classes"""

        extra = Extra.ignore


class ReqSignUp(BaseSignUp, ReqMeta):
    password: str


class RespSignUp(BaseSignUp, RespData):
    id: int
    status: UserStatus
    token: str


class ReqSignIn(ReqMeta):
    email: str
    password: str
    token: str
