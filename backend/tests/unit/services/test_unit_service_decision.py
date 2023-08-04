from collections import defaultdict
from decimal import Decimal
from typing import Self

import pytest
from uuid6 import UUID

from app.domain.decision import DomainDecision
from app.domain.iteration import DomainIteration
from app.infrastructure.repositories.base import Repository
from app.infrastructure.units_of_work.base import UnitOfWork
from app.services.decision import ServiceDecision
from app.system.constants import DecisionAction


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
