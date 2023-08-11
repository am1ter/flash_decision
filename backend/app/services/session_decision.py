from __future__ import annotations

from asyncio import TaskGroup
from typing import TYPE_CHECKING, Annotated

import structlog
from fastapi import Depends

from app.domain.session_decision import DomainDecision
from app.domain.session_result import SessionResult
from app.infrastructure.repositories.session import RepositorySessionSql
from app.infrastructure.units_of_work.base_sql import UnitOfWorkSqlAlchemy
from app.system.constants import DecisionAction, SessionStatus

if TYPE_CHECKING:
    from decimal import Decimal

    from app.domain.session import DomainSession
    from app.domain.session_iteration import DomainIteration
    from app.services.scoreboard import ServiceScoreboard

# Create logger
logger = structlog.get_logger()

# Internal dependencies
uow_session = UnitOfWorkSqlAlchemy(repository_type=RepositorySessionSql)
UowSessionDep = Annotated[UnitOfWorkSqlAlchemy, Depends(uow_session)]


class ServiceDecision:
    """
    This service records decisions for every `Iteration` in the `Session`.
    This service use Observer pattern implementation and acts as the Publisher.
    `ServiceScoreboard`s act as Subscribers.
    https://refactoring.guru/design-patterns/observer
    """

    __globals__ = globals()  # Bug workaround: https://github.com/tiangolo/fastapi/discussions/9085

    def __init__(self, uow: UowSessionDep) -> None:
        self.uow = uow
        self.scoreboard_services: list[ServiceScoreboard] = []  # list of Subscribers

    def register_scoreboard_service(self, scoreboard_service: ServiceScoreboard) -> None:
        self.scoreboard_services.append(scoreboard_service)

    async def _notify_scoreboard_services(self, session: DomainSession) -> None:
        if session.status != SessionStatus.closed:
            return
        session_result = SessionResult.create(session)
        for scoreboard_service in self.scoreboard_services:
            await scoreboard_service.update_scoreboard(session_result)

    def _update_session_status(self, session: DomainSession, iteration: DomainIteration) -> None:
        last_iteration_num = session.iterations.value - 1
        assert iteration.iteration_num <= last_iteration_num
        if iteration.iteration_num == 0:
            session.set_status_active()
        if iteration.iteration_num == last_iteration_num:
            session.set_status_closed()

    async def _save_decision_to_sql(self, decision: DomainDecision) -> None:
        async with self.uow:
            self.uow.repository.add(decision)
            await self.uow.commit()

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
        try:
            async with TaskGroup() as task_group:
                task_group.create_task(self._save_decision_to_sql(decision))
                task_group.create_task(self._notify_scoreboard_services(session))
        except ExceptionGroup as eg:
            raise eg.exceptions[0] from eg
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, decision=decision)
        return decision
