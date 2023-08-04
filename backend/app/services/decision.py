from decimal import Decimal
from typing import Annotated

import structlog
from fastapi import Depends

from app.domain.decision import DomainDecision
from app.domain.iteration import DomainIteration
from app.domain.session import DomainSession
from app.infrastructure.repositories.decision import RepositoryDecisionSql
from app.infrastructure.units_of_work.base_sql import UnitOfWorkSqlAlchemy
from app.system.constants import DecisionAction

# Create logger
logger = structlog.get_logger()

# Internal dependencies
uow_decision = UnitOfWorkSqlAlchemy(repository_type=RepositoryDecisionSql)
UowDecisionDep = Annotated[UnitOfWorkSqlAlchemy, Depends(uow_decision)]


class ServiceDecision:
    """This service records decisions for every Iteration in the Session."""

    def __init__(self, uow: UowDecisionDep) -> None:
        self.uow = uow

    async def record_decision(
        self,
        session: DomainSession,
        iteration: DomainIteration,
        action: DecisionAction,
        time_spent: Decimal,
    ) -> DomainDecision:
        decision = DomainDecision(
            session=session, iteration=iteration, action=action, time_spent=time_spent
        )
        async with self.uow:
            self.uow.repository.add(decision)
            await self.uow.commit()
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, decision=decision)
        return decision
