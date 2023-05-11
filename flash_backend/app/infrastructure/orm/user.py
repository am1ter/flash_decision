from typing import Annotated

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.user import DomainUser, UserStatus
from app.infrastructure.orm.base import Base, mapper_registry, str_unq
from app.system.config import settings_db

user_status = Annotated[
    UserStatus,
    mapped_column(
        Enum(UserStatus, name="user_status", schema=settings_db.DB_SCHEMA),
        nullable=False,
        default=UserStatus.active.value,
    ),
]


class OrmUser(Base):
    """
    ORM object `User` is used to identify individuals who use application.
    Sign up is available for everyone, but not required (there is a demo user).
    All users have the same privileges.
    """

    name: Mapped[str]
    email: Mapped[str_unq]
    password: Mapped[str]
    status: Mapped[user_status]


# Domain <-> ORM models mapping
mapper_registry.map_imperatively(DomainUser, OrmUser)
