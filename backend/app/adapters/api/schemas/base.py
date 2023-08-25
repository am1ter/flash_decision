from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


class RespMeta(BaseModel):
    """Container for sending Request's meta data to a client"""

    # Allow to receive custom attributes during instance creation
    model_config = ConfigDict(extra="allow")


class RespData(BaseModel):
    """Container for sending Request's data to a client"""


# Create a generic type variables for the response models
Rm = TypeVar("Rm", bound=RespMeta)
Rd = TypeVar("Rd", bound=RespData)


class Resp(BaseModel, Generic[Rm, Rd]):
    """Format every API response with JSON:API specification format (https://jsonapi.org)"""

    meta: Rm | None = None
    data: Rd
