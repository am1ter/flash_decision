from collections import defaultdict
from copy import deepcopy
from decimal import Decimal
from typing import TYPE_CHECKING, Self

import pytest

from app.domain.session_decision import DomainDecision
from app.domain.session_iteration import DomainIteration
from app.infrastructure.repositories.base import Repository
from app.infrastructure.units_of_work.base import UnitOfWork
from app.services.session_decision import ServiceDecision
from app.system.constants import DecisionAction, SessionStatus
from app.system.exceptions import WrongDecisionError

if TYPE_CHECKING:
    from uuid import UUID


class RepositoryNoSqlDecisionFake(Repository):
    def __init__(self) -> None:
        self.storage: dict[UUID, dict[int, DomainDecision]] = defaultdict(dict)

    def add(self, obj: DomainDecision) -> None:  # type: ignore[override]
        self.storage[obj.session._id][obj.iteration.iteration_num] = obj


class UnitOfWorkDecisionFake(UnitOfWork):
    def __init__(self) -> None:
        self.repository = RepositoryNoSqlDecisionFake()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        pass

    async def commit(self) -> None:
        pass


@pytest.fixture(scope="class")
def service_decision() -> ServiceDecision:
    return ServiceDecision(UnitOfWorkDecisionFake())  # type: ignore[arg-type]


class TestServiceDecision:
    @pytest.mark.asyncio()
    async def test_record_decision_buy(
        self, service_decision: ServiceDecision, iteration: DomainIteration
    ) -> None:
        decision = await service_decision.record_decision(
            session=iteration.session,  # type: ignore[arg-type]
            iteration=iteration,
            action=DecisionAction.buy,
            time_spent=Decimal(5),
        )
        assert isinstance(decision, DomainDecision)
        assert round(iteration.df_quotes["close"].sum()) == 58837, "Incorrect mock iteration df"
        assert decision.result_raw == Decimal("-0.185969")
        assert decision.result_final == Decimal("-0.190969")

    @pytest.mark.asyncio()
    async def test_record_decision_skip(
        self, service_decision: ServiceDecision, iteration: DomainIteration
    ) -> None:
        decision = await service_decision.record_decision(
            session=iteration.session,  # type: ignore[arg-type]
            iteration=iteration,
            action=DecisionAction.skip,
            time_spent=Decimal(5),
        )
        assert isinstance(decision, DomainDecision)
        assert decision.result_raw == Decimal("0")
        assert decision.result_final == Decimal("0")

    @pytest.mark.asyncio()
    async def test_record_decision_sell(
        self, service_decision: ServiceDecision, iteration: DomainIteration
    ) -> None:
        decision = await service_decision.record_decision(
            session=iteration.session,  # type: ignore[arg-type]
            iteration=iteration,
            action=DecisionAction.sell,
            time_spent=Decimal(5),
        )
        assert isinstance(decision, DomainDecision)
        assert round(iteration.df_quotes["close"].sum()) == 58837, "Incorrect mock iteration df"
        assert decision.result_raw == Decimal("0.185969")
        assert decision.result_final == Decimal("0.180969")

    @pytest.mark.asyncio()
    async def test_record_decision_status_active(
        self, service_decision: ServiceDecision, iteration: DomainIteration
    ) -> None:
        assert iteration.session
        assert iteration.session.status == SessionStatus.created
        decision = await service_decision.record_decision(
            session=iteration.session,  # type: ignore[arg-type]
            iteration=iteration,
            action=DecisionAction.buy,
            time_spent=Decimal(5),
        )
        assert isinstance(decision, DomainDecision)
        assert iteration.session.status == SessionStatus.active

    @pytest.mark.asyncio()
    async def test_record_decision_status_closed(
        self, service_decision: ServiceDecision, iteration: DomainIteration
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
        assert isinstance(decision, DomainDecision)
        assert iteration.session.status == SessionStatus.closed

    @pytest.mark.asyncio()
    async def test_record_decision_status_closed_failure(
        self, service_decision: ServiceDecision, iteration: DomainIteration
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
