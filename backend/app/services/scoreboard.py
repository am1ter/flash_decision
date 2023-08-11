from abc import ABCMeta, abstractmethod
from typing import Annotated, cast

import structlog
from fastapi import Depends

from app.domain.scoreboard import ScoreboardRecordsTop
from app.domain.session_result import SessionResult
from app.domain.user import DomainUser
from app.infrastructure.repositories.scoreboard import RepositoryNoSqlScoreboard
from app.infrastructure.units_of_work.base_nosql import UnitOfWorkNoSqlMongo
from app.system.config import Settings
from app.system.constants import SessionMode
from app.system.exceptions import DbObjectNotFoundError

# Create logger
logger = structlog.get_logger()

# Internal dependencies
uow_scoreboard = UnitOfWorkNoSqlMongo(repository_type=RepositoryNoSqlScoreboard)
UowScoreboardDep = Annotated[UnitOfWorkNoSqlMongo, Depends(uow_scoreboard)]


class ServiceScoreboard(metaclass=ABCMeta):
    """
    Multiple different `ServiceScoreboard` implementations allowed.
    This service acts as the Subscriber of the Observer design pattern.
    `ServiceDecision` is the publisher, that pushed updates to this service.
    https://refactoring.guru/design-patterns/observer
    """

    @abstractmethod
    async def update_scoreboard(self, session_result: SessionResult) -> None:
        pass


class ServiceScoreboardGlobal(ServiceScoreboard):
    def __init__(self, uow: UowScoreboardDep) -> None:
        self.uow = uow

    async def update_scoreboard(self, session_result: SessionResult) -> None:
        async with self.uow:
            self.uow.repository = cast(RepositoryNoSqlScoreboard, self.uow.repository)
            updated_score = self.uow.repository.update_score(session_result)
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, score=updated_score)

    async def show_top_users(self, mode: SessionMode) -> ScoreboardRecordsTop | None:
        async with self.uow:
            self.uow.repository = cast(RepositoryNoSqlScoreboard, self.uow.repository)
            try:
                scoreboard_records = self.uow.repository.get_full_scoreboard(mode)
            except DbObjectNotFoundError:
                top_users = None
            else:
                scoreboard_records_top = scoreboard_records[: Settings().general.TOP_USER_COUNT]
                top_users = ScoreboardRecordsTop.create_from_records(scoreboard_records_top)
        await logger.ainfo_finish(
            cls=self.__class__, show_func_name=True, mode=mode, top_users=top_users
        )
        return top_users

    async def get_user_rank(self, user: DomainUser, mode: SessionMode) -> int | None:
        async with self.uow:
            self.uow.repository = cast(RepositoryNoSqlScoreboard, self.uow.repository)
            try:
                user_scoreboard_record = self.uow.repository.get_scoreboard_record(user, mode)
            except DbObjectNotFoundError:
                user_rank = None
            else:
                scoreboard_records = self.uow.repository.get_full_scoreboard(mode)
                user_rank = scoreboard_records.find_user_rank(user_scoreboard_record)
        await logger.ainfo_finish(
            cls=self.__class__, show_func_name=True, mode=mode, user_rank=user_rank
        )
        return user_rank
