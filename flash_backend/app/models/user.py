from enum import Enum
from typing import Annotated

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app.config import settings_db
from app.models.base import Base, datetime_current, int_pk, str_unq


class UserStatus(Enum):
    active = "active"
    disabled = "disabled"


user_status = Annotated[
    UserStatus,
    mapped_column(
        ENUM(*UserStatus.__members__, name="user_status", schema=settings_db.DB_SCHEMA),
        nullable=False,
        default=UserStatus.active.value,
    ),
]


class User(Base):
    Id: Mapped[int_pk]
    Name: Mapped[str]
    Email: Mapped[str_unq]
    Password: Mapped[str]
    DatetimeCreate: Mapped[datetime_current]
    Status: Mapped[user_status]
