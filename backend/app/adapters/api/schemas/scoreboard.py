from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.adapters.api.schemas.base import RespData


class TopUserRec(BaseModel):
    mode: str
    user_name: str
    result: Decimal


class TopUsers(BaseModel):
    records: dict[int, TopUserRec]


class UserModeSummery(BaseModel):
    mode: str
    total_sessions: int
    profitable_sessions: int
    unprofitable_sessions: int
    total_result: Decimal
    median_result: Decimal
    best_session_result: Decimal
    first_session_date: datetime


class UserRank(BaseModel):
    mode: str
    rank: int


class RespScoreboard(RespData):
    top_users: TopUsers | None
    user_mode_summary: UserModeSummery | None
    user_rank: UserRank | None
