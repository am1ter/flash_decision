from decimal import Decimal
from statistics import median
from typing import Self
from uuid import UUID

from attrs import define, field, validators

from app.domain.session import Session
from app.system.constants import DecisionAction, SessionMode, SessionStatus
from app.system.exceptions import SessionNotClosedError, WrongSessionResultError


@define
class SessionResult:
    """
    This class used to render the page with Session's results.
    Session's result is the summary of all User's Decisions.
    It is not an ORM object - db is not used for storing sessions' results.
    """

    session: Session = field(metadata={"asdict_ignore": True})
    total_decisions: int = field()
    profitable_decisions: int = field(validator=validators.ge(0))
    unprofitable_decisions: int = field(validator=validators.ge(0))
    skipped_decisions: int = field(validator=validators.ge(0))
    total_result: Decimal
    median_decisions_result: Decimal
    best_decisions_result: Decimal = field()
    worst_decisions_result: Decimal = field()
    total_time_spent: Decimal = field()
    session_id: UUID = field()
    mode: SessionMode = field()

    @session_id.default
    def session_id_default(self) -> UUID:
        return self.session._id

    @mode.default
    def mode_default(self) -> SessionMode:
        return self.session.mode

    @session.validator
    def session_validator(self, attribute: str, value: Session) -> None:
        if value.status != SessionStatus.closed:
            raise SessionNotClosedError

    @total_decisions.validator
    def total_decisions_validator(self, attribute: str, value: int) -> None:
        cnt = sum((self.profitable_decisions, self.unprofitable_decisions, self.skipped_decisions))
        if value != cnt:
            raise WrongSessionResultError

    @best_decisions_result.validator
    def best_decisions_result_validator(self, attribute: str, value: Decimal) -> None:
        if any((value < self.median_decisions_result, value < self.worst_decisions_result)):
            raise WrongSessionResultError

    @worst_decisions_result.validator
    def worst_decisions_result_validator(self, attribute: str, value: Decimal) -> None:
        if any((value > self.median_decisions_result, value > self.best_decisions_result)):
            raise WrongSessionResultError

    @total_time_spent.validator
    def total_time_spent_validator(self, attribute: str, value: Decimal) -> None:
        if value < 0:
            raise WrongSessionResultError

    @classmethod
    def create(cls, session: Session) -> Self:
        if session.status != SessionStatus.closed or not session.decisions:
            raise SessionNotClosedError

        profitable_decisions = 0
        unprofitable_decisions = 0
        skipped_decisions = 0
        total_result = Decimal("0")
        best_decisions_result = Decimal("-inf")
        worst_decisions_result = Decimal("inf")
        total_time_spent = Decimal("0")

        for decision in session.decisions:
            profitable_decisions += 1 if decision.result_final > 0 else 0
            unprofitable_decisions += 1 if decision.result_final <= 0 else 0
            skipped_decisions += 1 if decision.action == DecisionAction.skip else 0
            total_result += decision.result_final
            if decision.result_final > best_decisions_result:
                best_decisions_result = decision.result_final
            if decision.result_final < worst_decisions_result:
                worst_decisions_result = decision.result_final
            total_time_spent += decision.time_spent

        return cls(
            session=session,
            total_decisions=len(session.decisions),
            profitable_decisions=profitable_decisions,
            unprofitable_decisions=unprofitable_decisions,
            skipped_decisions=skipped_decisions,
            total_result=total_result,
            best_decisions_result=best_decisions_result,
            worst_decisions_result=worst_decisions_result,
            median_decisions_result=median([d.result_final for d in session.decisions]),
            total_time_spent=total_time_spent,
        )
