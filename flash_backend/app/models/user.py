from enum import Enum

from sqlalchemy.orm import Mapped

from app.models.base import Base, datetime_current, int_pk, str_unq


class UserStatus(Enum):
    active = "active"
    disabled = "disabled"


class User(Base):
    Id: Mapped[int_pk]
    Name: Mapped[str]
    Email: Mapped[str_unq]
    Password: Mapped[str]
    DatetimeCreate: Mapped[datetime_current]
    Status: Mapped[UserStatus]
