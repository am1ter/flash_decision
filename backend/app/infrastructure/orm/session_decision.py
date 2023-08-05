from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.orm.base import Base, datetime_current, mapped_column_enum, uuid_pk
from app.system.config import Settings
from app.system.constants import DecisionAction


class OrmDecision(Base):
    """
    The ORM object `Decision` is used to store it's parameters.
    """

    _id: Mapped[uuid_pk]
    datetime_create: Mapped[datetime_current]
    session_id: Mapped[str] = mapped_column(
        ForeignKey(f"{Settings().sql.SQL_DB_SCHEMA}.session._id", ondelete="CASCADE"), index=True
    )
    iteration_num: Mapped[int]
    time_spent: Mapped[Decimal]
    result_raw: Mapped[Decimal]
    result_final: Mapped[Decimal]
    action: Mapped[DecisionAction] = mapped_column_enum(DecisionAction)
