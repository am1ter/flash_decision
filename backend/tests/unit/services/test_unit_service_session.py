from typing import Self
from uuid import UUID

import pytest

from app.api.schemas.session import ReqSession
from app.domain.interfaces.repository import RepositorySession
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.domain.session import Session
from app.domain.user import User
from app.services.session import ServiceSession, SessionParams
from app.system.constants import SessionMode

pytestmark = pytest.mark.asyncio


class RepositorySessionFake(RepositorySession):
    def __init__(self) -> None:
        self.storage: dict[UUID, Session] = {}

    def add(self, obj: Session) -> None:  # type: ignore[override]
        self.storage[obj._id] = obj

    async def get_by_id(self, _id: UUID) -> Session:
        return self.storage[_id]

    async def get_all_sessions_by_user(self, user: User) -> list[Session]:
        return list(self.storage.values())


class UnitOfWorkSessionFake(UnitOfWork):
    def __init__(self) -> None:
        self.repository = RepositorySessionFake()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        pass

    async def commit(self) -> None:
        pass


@pytest.fixture()
def service_session() -> ServiceSession:
    return ServiceSession(UnitOfWorkSessionFake())  # type: ignore[arg-type]


class TestServiceSession:
    async def test_collect_session_options(self, service_session: ServiceSession) -> None:
        options = await service_session.collect_session_options()
        assert options
        assert len(options.all_ticker) > 100
        assert len(options.all_barsnumber) == 4
        assert options

    @pytest.mark.parametrize("mode", list(SessionMode))
    async def test_create_session(
        self,
        mode: SessionMode,
        service_session: ServiceSession,
        req_session_params_custom: ReqSession,
        user_domain: User,
    ) -> None:
        if mode == SessionMode.custom:
            params = SessionParams(**req_session_params_custom.dict())
        else:
            params = None
        session_quotes = await service_session.create_session(mode, params, user_domain)
        assert session_quotes.session
        assert not session_quotes.df_quotes.empty

    async def test_get_session(
        self,
        service_session: ServiceSession,
        req_session_params_custom: ReqSession,
        user_domain: User,
    ) -> None:
        # Create session
        params = SessionParams(**req_session_params_custom.dict())
        session_quotes = await service_session.create_session(
            SessionMode.custom, params, user_domain
        )
        assert session_quotes.session

        # Test get session
        session = await service_session.get_session(session_quotes.session._id, user_domain)
        assert session == session_quotes.session

    async def test_calc_session_result(
        self, service_session: ServiceSession, closed_session: Session
    ) -> None:
        session_result = await service_session.calc_session_result(closed_session)
        assert session_result.total_decisions == closed_session.iterations.value

    @pytest.mark.asyncio()
    async def test_calc_user_mode_summary(
        self, service_session: ServiceSession, closed_session: Session
    ) -> None:
        service_session.uow.repository.add(closed_session)
        user_mode_summary = await service_session.calc_user_mode_summary(
            closed_session.user, SessionMode.custom
        )
        assert user_mode_summary
        assert user_mode_summary.user == closed_session.user
        assert user_mode_summary.total_sessions == 1
