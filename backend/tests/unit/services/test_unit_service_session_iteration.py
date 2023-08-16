import json
from collections import defaultdict
from copy import deepcopy
from typing import Self
from uuid import UUID

import pytest

from app.domain.session import SessionQuotes
from app.domain.session_iteration import DomainIteration
from app.infrastructure.repositories.base import Repository
from app.infrastructure.units_of_work.base import UnitOfWork
from app.services.session_iteration import ServiceIteration
from app.system.constants import SessionStatus
from app.system.exceptions import SessionClosedError


class RepositoryNoSqlIterationFake(Repository):
    def __init__(self) -> None:
        self.storage: dict[UUID, dict[int, DomainIteration]] = defaultdict(dict)

    def add(self, obj: DomainIteration) -> None:  # type: ignore[override]
        self.storage[obj.session_id][obj.iteration_num] = obj

    def get_iteration(self, session_id: UUID, iteration_num: int) -> DomainIteration:
        return self.storage[session_id][iteration_num]


class UnitOfWorkIterationFake(UnitOfWork):
    def __init__(self) -> None:
        self.repository = RepositoryNoSqlIterationFake()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        pass


@pytest.fixture(scope="class")
def service_iteration() -> ServiceIteration:
    return ServiceIteration(UnitOfWorkIterationFake())  # type: ignore[arg-type]


class TestServiceIteration:
    @pytest.mark.dependency()
    @pytest.mark.asyncio()
    async def test_create_iterations(
        self, service_iteration: ServiceIteration, session_quotes: SessionQuotes
    ) -> None:
        iteration_collection = await service_iteration.create_iterations(session_quotes)
        assert len(iteration_collection) == session_quotes.session.iterations.value
        assert isinstance(iteration_collection[0], DomainIteration)

    @pytest.mark.dependency(depends=["TestServiceIteration::test_create_iterations"])
    @pytest.mark.asyncio()
    async def test_get_iteration(self, service_iteration: ServiceIteration) -> None:
        session_id = list(service_iteration.uow.repository.storage.keys())[0]  # type: ignore[attr-defined]
        iteration_num = 0
        iteration = await service_iteration._load_iteration(session_id, iteration_num)
        assert isinstance(iteration, DomainIteration)
        assert iteration.iteration_num == iteration_num

    @pytest.mark.dependency(depends=["TestServiceIteration::test_create_iterations"])
    @pytest.mark.asyncio()
    async def test_get_next_iteration_success(self, service_iteration: ServiceIteration) -> None:
        session_id = list(service_iteration.uow.repository.storage)[0]  # type: ignore[attr-defined]
        session = service_iteration.uow.repository.storage[session_id][0].session  # type: ignore[attr-defined]
        iteration = await service_iteration.get_next_iteration(session)
        assert isinstance(iteration, DomainIteration)
        assert "data" in json.loads(iteration.chart)

    @pytest.mark.dependency(depends=["TestServiceIteration::test_create_iterations"])
    @pytest.mark.asyncio()
    async def test_get_next_iteration_failure_closed(
        self, service_iteration: ServiceIteration
    ) -> None:
        session_id = list(service_iteration.uow.repository.storage)[0]  # type: ignore[attr-defined]
        session = deepcopy(service_iteration.uow.repository.storage[session_id][0].session)  # type: ignore[attr-defined]
        session.status = SessionStatus.closed
        with pytest.raises(SessionClosedError):
            await service_iteration.get_next_iteration(session)
