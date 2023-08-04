from typing import Self

import pytest
from uuid6 import UUID

from app.api.schemas.session import ReqSession
from app.domain.session import DomainSession
from app.domain.user import DomainUser
from app.infrastructure.repositories.base import Repository
from app.infrastructure.units_of_work.base import UnitOfWork
from app.services.session import ServiceSession, SessionParams
from app.system.constants import SessionMode

pytestmark = pytest.mark.asyncio


class RepositorySessionFake(Repository):
    def __init__(self) -> None:
        self.storage: dict[UUID, DomainSession] = {}

    def add(self, obj: DomainSession) -> None:  # type: ignore[override]
        self.storage[obj._id] = obj

    async def get_by_id(self, _id: UUID) -> DomainSession:
        return self.storage[_id]


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
        user_domain: DomainUser,
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
        user_domain: DomainUser,
    ) -> None:
        # Create session
        params = SessionParams(**req_session_params_custom.dict())
        session_quotes = await service_session.create_session(
            SessionMode.custom, params, user_domain
        )
        assert session_quotes.session

        # Test get session
        session = await service_session.get_session(session_quotes.session._id)
        assert session == session_quotes.session
