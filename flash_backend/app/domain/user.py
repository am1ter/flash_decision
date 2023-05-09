from enum import Enum

from attrs import define, field

from app.domain.base import Entity


class UserStatus(Enum):
    active = "active"
    disabled = "disabled"


@define(kw_only=True, hash=True)
class User(Entity):
    name: str
    email: str
    password: str
    status: UserStatus = field(converter=UserStatus)
