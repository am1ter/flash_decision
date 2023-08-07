from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel


class RespMeta(BaseModel):
    """Container for sending Request's meta data to a client"""


class RespData(BaseModel):
    """Container for sending Request's data to a client"""


# Create a generic type variables for the response models
Rm = TypeVar("Rm", bound=RespMeta)
Rd = TypeVar("Rd", bound=RespData)


class Resp(GenericModel, Generic[Rm, Rd]):
    """Format every API response with JSON:API specification format (https://jsonapi.org)"""

    meta: Rm | None = None
    data: Rd
