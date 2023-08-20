from bisect import bisect_left
from collections import UserDict, UserList
from decimal import Decimal
from typing import Self
from uuid import UUID

from attrs import define

from app.domain.interfaces.domain import Entity
from app.system.constants import SessionMode


@define
class ScoreboardRecord(Entity):
    """Scoreboard records stored in the database"""

    mode: SessionMode
    user_id: UUID
    user_name: str
    result: Decimal

    def __lt__(self, other: Self) -> bool:
        return self.result < other.result


class ScoreboardRecords(UserList):
    """Container for all scoreboard records extracted from the database"""

    data: list[ScoreboardRecord]

    def find_user_rank(self, user_scoreboard_record: ScoreboardRecord) -> int:
        return bisect_left(self, user_scoreboard_record)


class ScoreboardRecordsTop(UserDict):
    """This class used only for the slice of `ScoreboardRecords` to avoid performance issues"""

    data: dict[int, ScoreboardRecord]

    @classmethod
    def create_from_records(cls, scoreboard_records: ScoreboardRecords) -> Self:
        return cls(enumerate(scoreboard_records))
