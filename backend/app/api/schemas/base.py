from typing import Generic, TypeVar

from pydantic import BaseModel, Extra
from pydantic.generics import GenericModel


class ReqMeta(BaseModel):
    class Config:
        extra = Extra.allow


class RespMeta(BaseModel):
    class Config:
        extra = Extra.allow


class RespData(BaseModel):
    class Config:
        extra = Extra.allow


# Create a generic type variable for the response model
Rm = TypeVar("Rm", bound=RespMeta)
Rd = TypeVar("Rd", bound=RespData)


class Resp(GenericModel, Generic[Rm, Rd]):
    meta: Rm | None = None
    data: Rd
