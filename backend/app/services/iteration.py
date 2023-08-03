from typing import Annotated, cast

import structlog
from fastapi import Depends
from uuid6 import UUID

from app.domain.iteration import DomainIteration, DomainIterationCollection
from app.domain.session import SessionQuotes
from app.infrastructure.repositories.iteration import RepositoryNoSqlIteration
from app.infrastructure.units_of_work.base_nosql import UnitOfWorkNoSqlMongo

# Create logger
logger = structlog.get_logger()

# Internal dependencies
uow_iteration = UnitOfWorkNoSqlMongo(repository_type=RepositoryNoSqlIteration)
UowIterationDep = Annotated[UnitOfWorkNoSqlMongo, Depends(uow_iteration)]


class ServiceIteration:
    """Decompose session into several parts - iterations"""

    def __init__(self, uow: UowIterationDep) -> None:
        self.uow = uow

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

    async def render_chart(self, session_id: UUID, iteration_num: int) -> str:
        iteration = await self.get_iteration(session_id=session_id, iteration_num=iteration_num)
        chart = iteration.render_chart()
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, iteration=iteration)
        return chart

    async def get_iteration(self, session_id: UUID, iteration_num: int) -> DomainIteration:
        async with self.uow:
            self.uow.repository = cast(RepositoryNoSqlIteration, self.uow.repository)
            iteration = self.uow.repository.get_iteration(session_id, iteration_num)
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, iteration=iteration)
        return iteration
