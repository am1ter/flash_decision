from typing import Annotated

from fastapi import Depends

from app.domain.user import DomainUser
from app.infrastructure.repositories.base import RepositorySQLAlchemy


class RepositoryUserSQL(RepositorySQLAlchemy):
    async def get_by_id(self, id: int) -> DomainUser | None:
        return await self._select_one(DomainUser.id, id)

    async def get_by_email(self, email: str) -> DomainUser | None:
        return await self._select_one(DomainUser.email, email)


# For dependency injection
repository_user = Annotated[RepositoryUserSQL, Depends()]
