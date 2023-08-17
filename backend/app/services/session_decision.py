from __future__ import annotations

from asyncio import TaskGroup
from typing import TYPE_CHECKING

import structlog
from attrs import define, field

from app.domain.session_decision import DomainDecision
from app.domain.session_result import SessionResult
from app.services.base import Service
from app.system.constants import DecisionAction, SessionStatus

if TYPE_CHECKING:
    from decimal import Decimal

    from app.domain.repository import RepositorySession
    from app.domain.session import DomainSession
    from app.domain.session_iteration import DomainIteration
    from app.domain.unit_of_work import UnitOfWork
    from app.services.scoreboard import ServiceScoreboard

# Create logger
logger = structlog.get_logger()


@define(kw_only=False, slots=False, hash=False)
class ServiceDecision(Service):
    """
    This service records decisions for every `Iteration` in the `Session`.
    This service use Observer pattern implementation and acts as the Publisher.
    `ServiceScoreboard`s act as Subscribers.
    https://refactoring.guru/design-patterns/observer
    """

    uow: UnitOfWork[RepositorySession]
    scoreboard_services: list[ServiceScoreboard] = field(factory=list)  # list of Subscribers

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
