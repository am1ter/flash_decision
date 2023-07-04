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


class SessionMode(str, Enum):
    classic = "classic"
    blitz = "blitz"
    crypto = "crypto"
    custom = "custom"


class SessionStatus(Enum):
    created = "created"
    active = "active"
    closed = "closed"


class SessionTimeframe(Enum):
    minutes1 = "1min"
    minutes5 = "5min"
    minutes15 = "15min"
    minutes30 = "30min"
    minutes60 = "60min"
    daily = "1day"


class SessionBarsnumber(Enum):
    bars15 = 15
    bars30 = 30
    bars50 = 50
    bars100 = 100


class SessionTimelimit(Enum):
    seconds5 = 5
    seconds10 = 10
    seconds30 = 30
    seconds60 = 60
    seconds120 = 120


class SessionIterations(Enum):
    iterations5 = 5
    iterations10 = 10
    iterations20 = 20
    iterations30 = 30


class SessionSlippage(Enum):
    """Slippage is also used as an imitation of all possible commissions (in percentages)"""

    no_slippage = 0
    low = 0.1
    average = 0.5
    high = 1


class SessionFixingbar(Enum):
    bar10 = 10
    bar20 = 20
    bar30 = 30
    bar50 = 50


class SessionTradingType(Enum):
    """Trading type is determined by using threshold value (in days)"""

    intraday = 1
    swingtrading = 30
    shortinvesting = 90
    longinvesting = float("inf")
