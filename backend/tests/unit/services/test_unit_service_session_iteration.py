import json
from collections import defaultdict
from copy import deepcopy
from typing import Self
from uuid import UUID

import pytest

from app.domain.repository import RepositoryIteration
from app.domain.session import SessionQuotes
from app.domain.session_iteration import Iteration, IterationCollection
from app.domain.unit_of_work import UnitOfWork
from app.services.session_iteration import ServiceIteration
from app.system.constants import SessionStatus
from app.system.exceptions import SessionClosedError


class RepositoryIterationFake(RepositoryIteration):
    def __init__(self) -> None:
        self.storage: dict[UUID, dict[int, Iteration]] = defaultdict(dict)

    def add(self, obj: Iteration) -> None:  # type: ignore[override]
        self.storage[obj.session_id][obj.iteration_num] = obj

    def get_iteration(self, session_id: UUID, iteration_num: int) -> Iteration:
        return self.storage[session_id][iteration_num]

    def get_iteration_collection(self, session_id: UUID) -> IterationCollection:  # type: ignore[empty-body]
        pass


class UnitOfWorkIterationFake(UnitOfWork):
    def __init__(self) -> None:
        self.repository = RepositoryIterationFake()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        pass

    async def commit(self) -> None:
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
        assert isinstance(iteration_collection[0], Iteration)

    @pytest.mark.dependency(depends=["TestServiceIteration::test_create_iterations"])
    @pytest.mark.asyncio()
    async def test_get_iteration(self, service_iteration: ServiceIteration) -> None:
        session_id = list(service_iteration.uow.repository.storage.keys())[0]  # type: ignore[attr-defined]
        iteration_num = 0
        iteration = await service_iteration._load_iteration(session_id, iteration_num)
        assert isinstance(iteration, Iteration)
        assert iteration.iteration_num == iteration_num

    @pytest.mark.dependency(depends=["TestServiceIteration::test_create_iterations"])
    @pytest.mark.asyncio()
    async def test_get_next_iteration_success(self, service_iteration: ServiceIteration) -> None:
        session_id = list(service_iteration.uow.repository.storage)[0]  # type: ignore[attr-defined]
        session = service_iteration.uow.repository.storage[session_id][0].session  # type: ignore[attr-defined]
        iteration = await service_iteration.get_next_iteration(session)
        assert isinstance(iteration, Iteration)
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
