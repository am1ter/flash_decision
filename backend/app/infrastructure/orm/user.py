from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm.base import Base, str_unq
from app.system.config import settings_db
from app.system.constants import AuthStatus, UserStatus


class OrmUser(Base):
    """
    The ORM object `User` is used to identify individuals who use the application.
    Sign up is available for everyone but not required (there is a demo user).
    All users have the same privileges.
    """

    name: Mapped[str]
    email: Mapped[str_unq] = mapped_column(key="_email")  # This col replaced with ValueObject
    password: Mapped[str] = mapped_column(key="_password")  # This col replaced with ValueObject
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status", schema=settings_db.DB_SCHEMA),
        nullable=False,
        default=UserStatus.active.value,
    )


class OrmAuth(Base):
    """
    The ORM object `Auth` is a record in the database with authentication information.
    It describes authentication attempts, including unsuccessful ones, as well as new sign-ups.
    """

    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{settings_db.DB_SCHEMA}.user.id", ondelete="CASCADE"), index=True
    )
    ip_address: Mapped[str] = mapped_column(key="_ip_address")  # This col replaced with ValueObject
    http_user_agent: Mapped[str]
    status: Mapped[AuthStatus] = mapped_column(
        Enum(AuthStatus, name="auth_status", schema=settings_db.DB_SCHEMA), nullable=False
    )
