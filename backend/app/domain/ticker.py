from typing import TypeAlias

from attrs import define, field, validators

from app.domain.interfaces.domain import ValueObjectJson
from app.system.constants import TickerType


@define
class Ticker(ValueObjectJson):
    ticker_type: TickerType = field(converter=TickerType)
    exchange: str
    symbol: str = field(validator=validators.min_len(1))
    name: str


tickers: TypeAlias = dict[str, Ticker]
