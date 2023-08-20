from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
from uuid6 import uuid6

from app.api.schemas.session import ReqSession
from app.api.schemas.user import ReqSignIn, ReqSignUp
from app.domain.session import Session, SessionCustom, SessionQuotes
from app.domain.session_decision import Decision
from app.domain.session_iteration import Iteration
from app.domain.session_result import SessionResult
from app.domain.ticker import Ticker
from app.domain.user import User
from app.system.constants import (
    DecisionAction,
    SessionBarsnumber,
    SessionFixingbar,
    SessionIterations,
    SessionMode,
    SessionSlippage,
    SessionStatus,
    SessionTimeframe,
    SessionTimelimit,
    TickerType,
    UserStatus,
)


@pytest.fixture()
def user_domain() -> User:
    return User(
        email=f"test-user-{uuid6()!s}@alekseisemenov.ru",
        name="test-user",
        password=str(uuid6()),
        status=UserStatus.active,
    )


def df_quotes_stocks() -> pd.DataFrame:
    path = Path(__file__).parent / "_mock_data" / "provider_av_stocks_mock_success_data.json"
    return pd.read_json(path)


def df_quotes_crypto() -> pd.DataFrame:
    path = Path(__file__).parent / "_mock_data" / "provider_av_crypto_mock_success_data.json"
    return pd.read_json(path)


@pytest.fixture()
def session(mock_ticker: Ticker, user_domain: User) -> Session:
    session = SessionCustom(
        mode=SessionMode.custom,
        ticker=mock_ticker,
        timeframe=SessionTimeframe.daily,
        barsnumber=SessionBarsnumber.bars70,
        timelimit=SessionTimelimit.seconds60,
        iterations=SessionIterations.iterations5,
        slippage=SessionSlippage.average,
        fixingbar=SessionFixingbar.bar20,
        status=SessionStatus.created,
    )
    session.user = user_domain
    return session


@pytest.fixture()
def session_quotes(session: Session) -> SessionQuotes:
    return SessionQuotes.create(session=session, df_quotes=df_quotes_stocks())


@pytest.fixture()
def iteration(session_quotes: SessionQuotes) -> Iteration:
    data_path = Path(__file__).parent / "_mock_data" / "mock_iteration_01.json"
    df_quotes_iteration = pd.read_json(data_path)
    return Iteration(
        session_id=session_quotes.session._id,
        iteration_num=0,
        df_quotes=df_quotes_iteration,
        session=session_quotes.session,
    )


@pytest.fixture()
def decision(iteration: Iteration) -> Decision:
    assert iteration.session
    return Decision(
        session=iteration.session,
        iteration=iteration,
        action=DecisionAction.buy,
        time_spent=Decimal("5"),
    )


@pytest.fixture()
def closed_session(session: Session, decision: Decision) -> Session:
    for _ in range(session.iterations.value - 1):
        session.decisions.append(decision)
    session.set_status_closed()
    return session


@pytest.fixture()
def session_result(closed_session: Session) -> SessionResult:
    return SessionResult.create(closed_session)


@pytest.fixture(scope="module")
def req_sign_up() -> ReqSignUp:
    return ReqSignUp(
        email=f"test-user-{uuid6()}@alekseisemenov.ru",
        name="test-user",
        password=str(uuid6()),
    )


@pytest.fixture(scope="module")
def req_sign_in(req_sign_up: ReqSignUp) -> ReqSignIn:
    return ReqSignIn(username=req_sign_up.email, password=req_sign_up.password)


@pytest.fixture()
def mock_ticker() -> Ticker:
    return Ticker(ticker_type=TickerType.stock, exchange="Mock", symbol="MOCK", name="Mock ticker")


@pytest.fixture(scope="module")
def req_session_params_custom() -> ReqSession:
    return ReqSession(
        mode=SessionMode.custom.value,
        ticker_type=TickerType.stock.value,
        ticker_symbol="AAPL",
        barsnumber=SessionBarsnumber.bars50.value,
        fixingbar=SessionFixingbar.bar20.value,
        iterations=SessionIterations.iterations5.value,
        slippage=SessionSlippage.low.value,
        timeframe=SessionTimeframe.minutes15.value,
        timelimit=SessionTimelimit.seconds60.value,
    )
