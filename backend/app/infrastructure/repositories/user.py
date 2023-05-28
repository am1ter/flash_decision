from typing import Annotated

from fastapi import Depends

from app.domain.user import DomainUser
from app.infrastructure.repositories.base import RepositorySQLAlchemy


class RepositoryUserSQL(RepositorySQLAlchemy):
    async def get_by_id(self, id: int) -> DomainUser:
        user = await self._select_one(DomainUser.id, id)
        assert isinstance(user, DomainUser)
        return user

    async def get_by_email(self, email: str) -> DomainUser:
        user = await self._select_one(DomainUser.email, email)
        assert isinstance(user, DomainUser)
        return user


# For dependency injection
RepositoryUserDep = Annotated[RepositoryUserSQL, Depends()]
