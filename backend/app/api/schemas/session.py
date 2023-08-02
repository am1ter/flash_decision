from pydantic import BaseModel

from app.api.schemas.base import RespData


class ReqSession(BaseModel):
    mode: str
    ticker_type: str
    ticker_symbol: str
    timeframe: str
    barsnumber: int
    timelimit: int
    iterations: int
    slippage: float
    fixingbar: int


class RespSessionOptions(RespData):
    all_ticker: list[dict[str, str]]
    all_timeframe: list[str]
    all_barsnumber: list[int]
    all_timelimit: list[int]
    all_iterations: list[int]
    all_slippage: list[float]
    all_fixingbar: list[int]


class RespSession(RespData):
    _id: str
    mode: str
    ticker_type: str
    ticker_symbol: str
    timeframe: str
    barsnumber: int
    timelimit: int
    iterations: int
    slippage: float
    fixingbar: int
    status: str
