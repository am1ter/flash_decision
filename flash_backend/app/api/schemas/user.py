from pydantic import BaseModel, Extra

from app.api.schemas.base import ReqMeta, RespData
from app.domain.user import UserStatus


class BaseUser(BaseModel):
    email: str
    name: str

    class Config:
        """Disable Extra.allow which is inherited from meta classes"""

        extra = Extra.ignore


class ReqSignUp(BaseUser, ReqMeta):
    password: str


class RespSignUp(BaseUser, RespData):
    id: int
    status: UserStatus
    token: str
