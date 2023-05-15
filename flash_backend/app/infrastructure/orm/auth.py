from typing import Annotated

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm.base import Base
from app.system.config import settings_db
from app.system.constants import AuthStatus

user_id = Annotated[
    int,
    mapped_column(ForeignKey(f"{settings_db.DB_SCHEMA}.user.id", ondelete="CASCADE"), index=True),
]
status = Annotated[
    AuthStatus,
    mapped_column(
        Enum(AuthStatus, name="auth_status", schema=settings_db.DB_SCHEMA), nullable=False
    ),
]


class OrmAuth(Base):
    """
    ORM object `Auth` is record in the db with auth info.
    It describe auth attempts (including unsuccessful ones) and new sign ups.
    """

    user_id: Mapped[user_id]
    ip_address: Mapped[str]
    http_user_agent: Mapped[str]
    status: Mapped[status]
