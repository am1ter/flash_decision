from abc import ABCMeta, abstractmethod
from typing import assert_never
from uuid import UUID

import structlog
from attrs import define

from app.domain.repository import RepositoryIteration
from app.domain.session import DomainSession, SessionQuotes
from app.domain.session_iteration import DomainIteration, DomainIterationCollection
from app.domain.unit_of_work import UnitOfWork
from app.services.base import Service
from app.system.constants import SessionStatus
from app.system.exceptions import SessionClosedError

# Create logger
logger = structlog.get_logger()


@define(kw_only=False, slots=False, hash=True)
class ServiceIteration(Service):
    """Decompose Session into several parts - Iterations"""

    uow: UnitOfWork[RepositoryIteration]

    async def create_iterations(self, session_quotes: SessionQuotes) -> DomainIterationCollection:
        iteration_collection = DomainIterationCollection(session_quotes=session_quotes)
        iteration_collection.create_iterations()
        async with self.uow:
            for iteration in iteration_collection.iterations:
                self.uow.repository.add(iteration)
        await logger.ainfo_finish(
            cls=self.__class__, show_func_name=True, iteration_collection=iteration_collection
        )
        return iteration_collection

    async def get_next_iteration(self, session: DomainSession) -> DomainIteration:
        loader: Loader
        match session.status:
            case SessionStatus.created:
                loader = LoaderSessionCreated()
            case SessionStatus.active:
                loader = LoaderSessionActive()
            case SessionStatus.closed:
                loader = LoaderSessionClosed()
            case _:
                assert_never(session.status)
        iteration = await loader.load_iteration(service=self, session=session)
        assert isinstance(iteration, DomainIteration)
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, iteration=iteration)
        return iteration

    async def _load_iteration(self, session_id: UUID, iteration_num: int) -> DomainIteration:
        async with self.uow:
            iteration = self.uow.repository.get_iteration(session_id, iteration_num)
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, iteration=iteration)
        return iteration


class Loader(metaclass=ABCMeta):
    """
    Interfacte for the State design pattern.
    Used to setup type of the behaviour during the request to extract Iterations from db.
    https://refactoring.guru/design-patterns/state
    """

    @abstractmethod
    async def load_iteration(
        self, service: ServiceIteration, session: DomainSession
    ) -> DomainIteration:
        pass


class LoaderSessionCreated(Loader):
    async def load_iteration(
        self, service: ServiceIteration, session: DomainSession
    ) -> DomainIteration:
        return await service._load_iteration(session_id=session._id, iteration_num=0)


class LoaderSessionActive(Loader):
    async def load_iteration(
        self, service: ServiceIteration, session: DomainSession
    ) -> DomainIteration:
        next_iter_num = len(session.decisions)
        if next_iter_num > session.iterations.value:
            raise SessionClosedError
        return await service._load_iteration(session_id=session._id, iteration_num=next_iter_num)


class LoaderSessionClosed(Loader):
    async def load_iteration(
        self, service: ServiceIteration, session: DomainSession
    ) -> DomainIteration:
        raise SessionClosedError
