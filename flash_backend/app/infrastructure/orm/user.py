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
    id: Mapped[int_pk]
    name: Mapped[str]
    email: Mapped[str_unq]
    password: Mapped[str]
    datetime_create: Mapped[datetime_current]
    status: Mapped[user_status]
