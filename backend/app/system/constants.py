from enum import Enum


class Environment(Enum):
    development = "development"
    production = "production"
    test = "test"


class UserStatus(Enum):
    active = "active"
    disabled = "disabled"


class AuthStatus(Enum):
    sign_up = "sign_up"
    sign_in = "sign_in"
    wrong_password = "wrong_password"  # noqa: S105


class TickerType(Enum):
    stock = "Stock"
    etf = "ETF"
    crypto = "Crypto"


class Timeframe(Enum):
    minutes1 = "1min"
    minutes5 = "5min"
    minutes15 = "15min"
    minutes30 = "30min"
    minutes60 = "60min"
    daily = "1day"
