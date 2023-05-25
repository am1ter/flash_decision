from typing import Generic, TypeVar

from pydantic import BaseModel, Extra
from pydantic.generics import GenericModel


class RespMeta(BaseModel):
    class Config:
        extra = Extra.allow  # Gives ability to inherit from this class and add additional attrs


class RespData(BaseModel):
    class Config:
        extra = Extra.allow  # Gives ability to inherit from this class and add additional attrs


# Create a generic type variables for the response models
Rm = TypeVar("Rm", bound=RespMeta)
Rd = TypeVar("Rd", bound=RespData)


class Resp(GenericModel, Generic[Rm, Rd]):
    """Format every API response with JSON:API specification format (https://jsonapi.org)"""

    meta: Rm | None = None
    data: Rd
