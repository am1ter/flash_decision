from collections import defaultdict
from decimal import Decimal
from typing import Self, cast

import pytest

from app.domain.base import Entity
from app.domain.scoreboard import ScoreboardRecord, ScoreboardRecords
from app.domain.session_result import SessionResult
from app.domain.user import DomainUser
from app.infrastructure.repositories.base import Repository
from app.infrastructure.units_of_work.base import UnitOfWork
from app.services.scoreboard import ServiceScoreboardGlobal
from app.system.constants import SessionMode


class RepositoryNoSqlScoreboardFake(Repository):
    def __init__(self) -> None:
        self.storage: dict[SessionMode, dict[DomainUser, ScoreboardRecord]] = defaultdict(dict)

    def add(self, obj: Entity) -> None:
        pass

    def update_score(self, session_result: SessionResult) -> Decimal:
        self.storage[session_result.mode][session_result.session.user] = ScoreboardRecord(
            mode=session_result.mode,
            user_id=session_result.session.user._id,
            user_name=session_result.session.user.name,
            result=session_result.total_result,
        )
        return self.storage[session_result.mode][session_result.session.user].result

    def get_full_scoreboard(self, mode: SessionMode) -> ScoreboardRecords:
        return ScoreboardRecords(self.storage[mode].values())

    def get_scoreboard_record(self, user: DomainUser, mode: SessionMode) -> ScoreboardRecord:
        return self.storage[mode][user]


class UnitOfWorkScoreboardFake(UnitOfWork):
    def __init__(self) -> None:
        self.repository = RepositoryNoSqlScoreboardFake()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        pass


@pytest.fixture(scope="class")
def service_scoreboard_global() -> ServiceScoreboardGlobal:
    return ServiceScoreboardGlobal(UnitOfWorkScoreboardFake())  # type: ignore[arg-type]


class TestServiceScoreboard:
    @pytest.mark.asyncio()
    @pytest.mark.dependency()
    async def test_update_scoreboard(
        self, service_scoreboard_global: ServiceScoreboardGlobal, session_result: SessionResult
    ) -> None:
        await service_scoreboard_global.update_scoreboard(session_result)
        repo = cast(RepositoryNoSqlScoreboardFake, service_scoreboard_global.uow.repository)
        user = list(repo.storage[SessionMode.custom].keys())[0]
        mode = session_result.mode
        assert repo.storage[mode][user].result == session_result.total_result

    @pytest.mark.asyncio()
    @pytest.mark.dependency(depends=["TestServiceScoreboard::test_update_scoreboard"])
    async def test_show_top_users(self, service_scoreboard_global: ServiceScoreboardGlobal) -> None:
        top_users = await service_scoreboard_global.show_top_users(SessionMode.custom)
        assert top_users
        repo = cast(RepositoryNoSqlScoreboardFake, service_scoreboard_global.uow.repository)
        user = list(repo.storage[SessionMode.custom].keys())[0]
        score_from_repo = repo.storage[SessionMode.custom][user]
        assert top_users[0] == score_from_repo

    @pytest.mark.asyncio()
    @pytest.mark.dependency(depends=["TestServiceScoreboard::test_update_scoreboard"])
    async def test_get_user_rank(self, service_scoreboard_global: ServiceScoreboardGlobal) -> None:
        repo = cast(RepositoryNoSqlScoreboardFake, service_scoreboard_global.uow.repository)
        user = list(repo.storage[SessionMode.custom].keys())[0]
        user_rank = await service_scoreboard_global.get_user_rank(user, SessionMode.custom)
        assert user_rank == 0
