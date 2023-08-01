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
        self.storage: dict[UUID, DomainIteration] = {}

    def add(self, obj: DomainIteration) -> None:  # type: ignore[override]
        self.storage[obj._id] = obj


class UnitOfWorkIterationFake(UnitOfWork):
    def __init__(self) -> None:
        self.repository = RepositoryNoSqlIterationFake()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        pass


@pytest.fixture()
def service_iteration() -> ServiceIteration:
    return ServiceIteration(UnitOfWorkIterationFake())  # type: ignore[arg-type]


class TestServiceIteration:
    @pytest.mark.asyncio()
    async def test_create_iterations(
        self, service_iteration: ServiceIteration, session_quotes: SessionQuotes
    ) -> None:
        iteration_collection = await service_iteration.create_iterations(session_quotes)
        assert len(iteration_collection) == session_quotes.session.iterations.value
        assert isinstance(iteration_collection[0], DomainIteration)
