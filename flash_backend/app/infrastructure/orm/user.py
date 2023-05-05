from typing import Annotated

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.user import UserStatus
from app.infrastructure.orm.base import Base, datetime_current, int_pk, str_unq
from app.system.config import settings_db

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
