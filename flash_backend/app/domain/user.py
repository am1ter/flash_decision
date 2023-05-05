from enum import Enum

from attr import define


class UserStatus(Enum):
    active = "active"
    disabled = "disabled"


@define
class User:
    Id: int
    Name: str
    Email: str
    Password: str
    DatetimeCreate: str
    Status: UserStatus
