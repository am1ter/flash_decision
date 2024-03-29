from copy import deepcopy
from decimal import Decimal

import pytest

from app.domain.session_decision import Decision
from app.domain.session_iteration import Iteration
from app.services.session_decision import ServiceDecision
from app.system.constants import DecisionAction, SessionStatus
from app.system.exceptions import WrongDecisionError
from tests.unit.services.test_unit_service_session import UnitOfWorkSessionFake


@pytest.fixture(scope="class")
def service_decision() -> ServiceDecision:
    return ServiceDecision(UnitOfWorkSessionFake())  # type: ignore[arg-type]


class TestServiceDecision:
    @pytest.mark.asyncio()
    async def test_record_decision_buy(
        self, service_decision: ServiceDecision, iteration: Iteration
    ) -> None:
        decision = await service_decision.record_decision(
            session=iteration.session,  # type: ignore[arg-type]
            iteration=iteration,
            action=DecisionAction.buy,
            time_spent=Decimal(5),
        )
        assert isinstance(decision, Decision)
        assert round(iteration.df_quotes["close"].sum()) == 58837, "Incorrect mock iteration df"
        assert decision.result_raw == Decimal("-0.185969")
        assert decision.result_final == Decimal("-0.190969")

    @pytest.mark.asyncio()
    async def test_record_decision_skip(
        self, service_decision: ServiceDecision, iteration: Iteration
    ) -> None:
        decision = await service_decision.record_decision(
            session=iteration.session,  # type: ignore[arg-type]
            iteration=iteration,
            action=DecisionAction.skip,
            time_spent=Decimal(5),
        )
        assert isinstance(decision, Decision)
        assert decision.result_raw == Decimal("0")
        assert decision.result_final == Decimal("0")

    @pytest.mark.asyncio()
    async def test_record_decision_sell(
        self, service_decision: ServiceDecision, iteration: Iteration
    ) -> None:
        decision = await service_decision.record_decision(
            session=iteration.session,  # type: ignore[arg-type]
            iteration=iteration,
            action=DecisionAction.sell,
            time_spent=Decimal(5),
        )
        assert isinstance(decision, Decision)
        assert round(iteration.df_quotes["close"].sum()) == 58837, "Incorrect mock iteration df"
        assert decision.result_raw == Decimal("0.185969")
        assert decision.result_final == Decimal("0.180969")

    @pytest.mark.asyncio()
    async def test_record_decision_status_active(
        self, service_decision: ServiceDecision, iteration: Iteration
    ) -> None:
        assert iteration.session
        assert iteration.session.status == SessionStatus.created
        decision = await service_decision.record_decision(
            session=iteration.session,  # type: ignore[arg-type]
            iteration=iteration,
            action=DecisionAction.buy,
            time_spent=Decimal(5),
        )
        assert isinstance(decision, Decision)
        assert iteration.session.status == SessionStatus.active

    @pytest.mark.asyncio()
    async def test_record_decision_status_closed(
        self, service_decision: ServiceDecision, iteration: Iteration
    ) -> None:
        assert iteration.session
        """Create all neccesary decisions to close the session"""
        for iter_num in range(iteration.session.iterations.value):
            new_iteration = deepcopy(iteration)
            new_iteration.iteration_num = iter_num
            decision = await service_decision.record_decision(
                session=iteration.session,  # type: ignore[arg-type]
                iteration=new_iteration,
                action=DecisionAction.buy,
                time_spent=Decimal(5),
            )
        assert isinstance(decision, Decision)
        assert iteration.session.status == SessionStatus.closed

    @pytest.mark.asyncio()
    async def test_record_decision_status_closed_failure(
        self, service_decision: ServiceDecision, iteration: Iteration
    ) -> None:
        """Try to record new decisionin closed session"""
        assert iteration.session
        new_iteration = deepcopy(iteration)
        new_iteration.iteration_num = iteration.session.iterations.value
        with pytest.raises(WrongDecisionError):
            await service_decision.record_decision(
                session=iteration.session,  # type: ignore[arg-type]
                iteration=new_iteration,
                action=DecisionAction.buy,
                time_spent=Decimal(5),
            )
