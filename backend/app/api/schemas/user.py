from pydantic import BaseModel, Extra, Field

from app.api.schemas.base import RespData
from app.domain.user import Email
from app.system.constants import UserStatus


class ReqSystemInfo(BaseModel):
    ip_address: str
    user_agent: str


class ReqSignUp(BaseModel):
    email: str
    name: str
    password: str = Field(repr=False)


class RespSignUp(RespData):
    id: int
    email: Email
    status: UserStatus
    token: str

    class Config:
        extra = Extra.ignore  # Disable `Extra.allow`` which is inherited from meta class
        arbitrary_types_allowed = True  # Add support for `attrs` classes


class ReqSignIn(BaseModel):
    email: str
    password: str = Field(repr=False)


class RespSignIn(RespData):
    email: Email
    status: UserStatus
    token: str

    class Config:
        extra = Extra.ignore  # Disable `Extra.allow`` which is inherited from meta class
        arbitrary_types_allowed = True  #  Add support for `attrs` classes
