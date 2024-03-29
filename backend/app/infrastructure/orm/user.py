from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm.base import Base, datetime_current, mapped_column_enum, str_unq, uuid_pk
from app.system.config import Settings
from app.system.constants import AuthStatus, UserStatus


class OrmUser(Base):
    """
    The ORM object `User` is used to identify individuals who use the application.
    Sign up is available for everyone but not required (there is a demo user).
    All users have the same privileges.
    """

    _id: Mapped[uuid_pk]
    datetime_create: Mapped[datetime_current]
    name: Mapped[str]
    email: Mapped[str_unq] = mapped_column(key="_email")  # This col replaced with ValueObject
    password: Mapped[str] = mapped_column(key="_password")  # This col replaced with ValueObject
    status: Mapped[UserStatus] = mapped_column_enum(UserStatus, UserStatus.active)


class OrmAuth(Base):
    """
    The ORM object `Auth` is a record in the database with authentication information.
    It describes authentication attempts, including unsuccessful ones, as well as new sign-ups.
    """

    _id: Mapped[uuid_pk]
    datetime_create: Mapped[datetime_current]
    user_id: Mapped[str] = mapped_column(
        ForeignKey(f"{Settings().sql.SQL_DB_SCHEMA}.user._id", ondelete="CASCADE"), index=True
    )
    ip_address: Mapped[str] = mapped_column(key="_ip_address")  # This col replaced with ValueObject
    http_user_agent: Mapped[str]
    status: Mapped[AuthStatus] = mapped_column_enum(AuthStatus)
