from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.adapters.api.schemas.base import RespData


class ReqSession(BaseModel):
    mode: str
    ticker_type: str
    ticker_symbol: str
    timeframe: str
    barsnumber: int
    timelimit: int
    iterations: int
    slippage: Decimal
    fixingbar: int


class RespSessionOptions(RespData):
    all_ticker: list[dict[str, str]]
    all_timeframe: list[str]
    all_barsnumber: list[int]
    all_timelimit: list[int]
    all_iterations: list[int]
    all_slippage: list[Decimal]
    all_fixingbar: list[int]


class RespSessionInfo(RespData):
    session_id: UUID
    mode: str
    ticker_type: str
    ticker_symbol: str
    timeframe: str
    barsnumber: int
    timelimit: int
    iterations: int
    slippage: Decimal
    fixingbar: int
    status: str


class RespSessionResult(BaseModel):
    session_id: UUID
    mode: str
    total_decisions: int
    profitable_decisions: int
    unprofitable_decisions: int
    skipped_decisions: int
    total_result: Decimal
    median_decisions_result: Decimal
    best_decisions_result: Decimal
    worst_decisions_result: Decimal
    total_time_spent: Decimal


class RespSession(RespData):
    info: RespSessionInfo | None
    result: RespSessionResult | None
