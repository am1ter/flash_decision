from pydantic import BaseModel, Extra, Field

from app.api.schemas.base import RespData


class ReqSystemInfo(BaseModel):
    ip_address: str
    user_agent: str


class ReqSignUp(BaseModel):
    email: str
    name: str
    password: str = Field(repr=False)


class RespSignUp(RespData):
    id: int
    email: str
    status: str
    token: str

    class Config:
        # Disable `Extra.allow`` which is inherited from meta class
        # It is important cases when used domain model unpacking using `**asdict()`
        extra = Extra.ignore


class ReqSignIn(BaseModel):
    email: str
    password: str = Field(repr=False)


class RespSignIn(RespData):
    email: str
    status: str
    token: str

    class Config:
        # Disable `Extra.allow`` which is inherited from meta class
        # It is important cases when used domain model unpacking using `**asdict()`
        extra = Extra.ignore
