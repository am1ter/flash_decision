from typing import Annotated

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.user import UserStatus
from app.infrastructure.orm.base import Base, str_unq
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
    """
    ORM object `User` is used to identify individuals who use application.
    Sign up is available for everyone, but not required (there is a demo user).
    All users have the same privileges.
    """

    name: Mapped[str]
    email: Mapped[str_unq]
    password: Mapped[str]
    status: Mapped[user_status]
