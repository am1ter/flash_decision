from asyncio import TaskGroup
from datetime import datetime
from random import randint
from typing import Self

import pytest

from app.api.schemas.session import ReqSession
from app.bootstrap import Bootstrap
from app.domain.session import DomainSession
from app.domain.user import DomainUser
from app.infrastructure.repositories.base import Repository
from app.infrastructure.units_of_work.base import UnitOfWork
from app.services.session import ServiceSession
from app.system.constants import SessionMode
from tests.conftest import ProviderAVCryptoMockSuccess, ProviderAVStocksMockSuccess

pytestmark = pytest.mark.asyncio


class RepositorySessionFake(Repository):
    def __init__(self) -> None:
        self.storage_session: dict[int, DomainSession] = {}

    def add(self, obj: DomainSession) -> None:  # type: ignore[override]
        if not hasattr(obj, "id"):
            obj.id = randint(1, 1000)
        obj.datetime_create = datetime.utcnow()
        self.storage_session[obj.id] = obj

    async def save(self) -> None:
        pass

    async def flush(self) -> None:
        pass

    async def refresh(self, object: DomainSession) -> None:
        pass

    async def get_by_id(self, id: int) -> DomainSession:
        return self.storage_session[id]


class UnitOfWorkSessionFake(UnitOfWork):
    def __init__(self) -> None:
        self.repository = RepositorySessionFake()
        self.task_group = TaskGroup()

    async def __aenter__(self) -> Self:
        await self.task_group.__aenter__()
        return await super().__aenter__()

    async def __aexit__(self, *args) -> None:
        await self.task_group.__aexit__(*args)
        await super().__aexit__(*args)

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


@pytest.fixture()
def service_session() -> ServiceSession:
    type(Bootstrap)._instances = {}
    Bootstrap(
        start_orm=False,
        cache=None,  # type: ignore[arg-type]
        provider_stocks=ProviderAVStocksMockSuccess(),
        provider_crypto=ProviderAVCryptoMockSuccess(),
    )
    return ServiceSession(UnitOfWorkSessionFake())  # type: ignore[arg-type]


class TestServiceSession:
    async def test_collect_session_options(self, service_session: ServiceSession) -> None:
        options = await service_session.collect_session_options()
        assert options
        assert len(options.all_ticker) > 100
        assert len(options.all_barsnumber) == 4
        assert options

    @pytest.mark.parametrize("mode", list(SessionMode))
    async def test_start_session(
        self,
        mode: SessionMode,
        service_session: ServiceSession,
        req_session_params_custom: ReqSession,
        user_domain: DomainUser,
    ) -> None:
        params = req_session_params_custom if mode == SessionMode.custom else None
        session = await service_session.start_session(mode, params, user_domain)
        assert not session.time_series.df.empty
        assert session
