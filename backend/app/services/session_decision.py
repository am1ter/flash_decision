from decimal import Decimal
from typing import Annotated

import structlog
from fastapi import Depends

from app.domain.session import DomainSession
from app.domain.session_decision import DomainDecision
from app.domain.session_iteration import DomainIteration
from app.infrastructure.repositories.session import RepositorySessionSql
from app.infrastructure.units_of_work.base_sql import UnitOfWorkSqlAlchemy
from app.system.constants import DecisionAction

# Create logger
logger = structlog.get_logger()

# Internal dependencies
uow_session = UnitOfWorkSqlAlchemy(repository_type=RepositorySessionSql)
UowSessionDep = Annotated[UnitOfWorkSqlAlchemy, Depends(uow_session)]


class ServiceDecision:
    """This service records decisions for every Iteration in the Session."""

    def __init__(self, uow: UowSessionDep) -> None:
        self.uow = uow

    def _update_session_status(self, session: DomainSession, iteration: DomainIteration) -> None:
        last_iteration_num = session.iterations.value - 1
        assert iteration.iteration_num <= last_iteration_num
        if iteration.iteration_num == 0:
            session.set_status_active()
        if iteration.iteration_num == last_iteration_num:
            session.set_status_closed()

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
        self._update_session_status(session, iteration)
        async with self.uow:
            self.uow.repository.add(decision)
            await self.uow.commit()
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, decision=decision)
        return decision
