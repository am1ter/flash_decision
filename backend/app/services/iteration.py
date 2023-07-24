from typing import Annotated

import structlog
from fastapi import Depends

from app.domain.iteration import DomainIterationCollection
from app.domain.session import DomainSession
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

    async def create_iterations(self, session: DomainSession) -> DomainIterationCollection:
        iteration_collection = DomainIterationCollection(session=session)
        iteration_collection.create_iterations()
        # Record iterations to NoSQL database
        async with self.uow:
            for iteration in iteration_collection.iterations:
                self.uow.repository.add(iteration)
        return iteration_collection
