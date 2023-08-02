from decimal import Decimal
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
    bars70 = 70


class SessionTimelimit(Enum):
    seconds5 = 5
    seconds10 = 10
    seconds30 = 30
    seconds60 = 60
    seconds120 = 120


class SessionIterations(Enum):
    iterations5 = 5
    iterations10 = 10
    iterations15 = 15
    iterations20 = 20


class SessionSlippage(Enum):
    """Used as an imitation of all commissions (decimal representation of the percentage)"""

    no_slippage = Decimal("0")
    low = Decimal("0.001")
    average = Decimal("0.005")
    high = Decimal("0.01")


class SessionFixingbar(Enum):
    bar10 = 10
    bar20 = 20
    bar30 = 30
    bar40 = 40


class SessionTradingType(Enum):
    """Trading type is determined by using threshold value (in days)"""

    intraday = 1
    swingtrading = 30
    shortinvesting = 90
    longinvesting = Decimal("inf")
