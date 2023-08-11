from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from statistics import median
from typing import Self

from attrs import define, field, validators

from app.domain.session import DomainSession
from app.domain.session_result import SessionResult
from app.domain.user import DomainUser
from app.system.constants import SessionMode, SessionStatus
from app.system.exceptions import NoUserModeSummaryError, WrongUserModeSummaryError


@define
class UserModeSummary:
    user: DomainUser
    mode: SessionMode
    total_sessions: int = field(validator=validators.ge(0))
    profitable_sessions: int = field(validator=validators.ge(0))
    unprofitable_sessions: int = field(validator=validators.ge(0))
    total_result: Decimal
    median_result: Decimal
    best_session_result: Decimal = field()
    first_session_date: datetime

    @best_session_result.validator
    def best_session_result_validator(self, attribute: str, value: Decimal) -> None:
        if value < self.median_result:
            raise WrongUserModeSummaryError

    @classmethod
    def create(cls, sessions: Sequence[DomainSession], mode: SessionMode) -> Self:
        session_results: list[SessionResult] = []
        profitable_sessions = 0
        unprofitable_sessions = 0
        total_result: Decimal = Decimal("0")
        best_session_result: Decimal = Decimal("-inf")
        first_session_date: datetime = datetime.utcnow()

        for session in sessions:
            if session.mode != mode or session.status != SessionStatus.closed:
                continue
            session_result = SessionResult.create(session)
            session_results.append(session_result)
            profitable_sessions += 1 if session_result.total_result > 0 else 0
            unprofitable_sessions += 1 if session_result.total_result <= 0 else 0
            total_result += session_result.total_result
            if session_result.total_result > best_session_result:
                best_session_result = session_result.total_result
            if session.datetime_create < first_session_date:
                first_session_date = session.datetime_create

        if not session_results:
            raise NoUserModeSummaryError

        return cls(
            user=session.user,
            mode=session.mode,
            total_sessions=len(session_results),
            profitable_sessions=profitable_sessions,
            unprofitable_sessions=unprofitable_sessions,
            total_result=total_result,
            median_result=median([sr.total_result for sr in session_results]),
            best_session_result=best_session_result,
            first_session_date=first_session_date,
        )
