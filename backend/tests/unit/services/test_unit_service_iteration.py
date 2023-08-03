import json
from collections import defaultdict
from typing import Self

import pytest
from uuid6 import UUID

from app.domain.iteration import DomainIteration
from app.domain.session import SessionQuotes
from app.infrastructure.repositories.base import Repository
from app.infrastructure.units_of_work.base import UnitOfWork
from app.services.iteration import ServiceIteration


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
        iteration = await service_iteration.get_iteration(session_id, iteration_num)
        assert isinstance(iteration, DomainIteration)
        assert iteration.iteration_num == iteration_num

    @pytest.mark.dependency(depends=["TestServiceIteration::test_create_iterations"])
    @pytest.mark.asyncio()
    async def test_render_chart(self, service_iteration: ServiceIteration) -> None:
        session_id = list(service_iteration.uow.repository.storage.keys())[0]  # type: ignore[attr-defined]
        iteration = await service_iteration.render_chart(session_id=session_id, iteration_num=0)
        assert "data" in json.loads(iteration)
