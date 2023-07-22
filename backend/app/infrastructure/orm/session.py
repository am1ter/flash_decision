from typing import ClassVar

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm.base import Base, datetime_current, jsonb, mapped_column_enum, uuid_pk
from app.system.config import Settings
from app.system.constants import (
    SessionBarsnumber,
    SessionFixingbar,
    SessionIterations,
    SessionMode,
    SessionSlippage,
    SessionStatus,
    SessionTimeframe,
    SessionTimelimit,
)


class OrmSession(Base):
    """
    The ORM object `Session` is used to store it's parameters.
    """

    __mapper_args__: ClassVar[dict[str, str]] = {"polymorphic_on": "mode"}

    _id: Mapped[uuid_pk]
    datetime_create: Mapped[datetime_current]
    user_id: Mapped[str] = mapped_column(
        ForeignKey(f"{Settings().sql.SQL_DB_SCHEMA}.user._id", ondelete="CASCADE"), index=True
    )
    ticker: Mapped[jsonb] = mapped_column(key="_ticker")  # ValueObject
    mode: Mapped[SessionMode] = mapped_column_enum(SessionMode)
    timeframe: Mapped[SessionTimeframe] = mapped_column_enum(SessionTimeframe)
    barsnumber: Mapped[SessionBarsnumber] = mapped_column_enum(SessionBarsnumber)
    timelimit: Mapped[SessionTimelimit] = mapped_column_enum(SessionTimelimit)
    iterations: Mapped[SessionIterations] = mapped_column_enum(SessionIterations)
    slippage: Mapped[SessionSlippage] = mapped_column_enum(SessionSlippage)
    fixingbar: Mapped[SessionFixingbar] = mapped_column_enum(SessionFixingbar)
    status: Mapped[SessionStatus] = mapped_column_enum(SessionStatus, SessionStatus.created)
