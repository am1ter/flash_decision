from typing import Annotated

from fastapi import Depends

from app.domain.user import DomainUser
from app.infrastructure.orm.user import OrmUser
from app.infrastructure.repositories.base import RepositorySQLAlchemy


class RepositoryUserSQL(RepositorySQLAlchemy):
    cls_domain = DomainUser
    cls_orm = OrmUser

    async def get_by_email(self, email: str) -> DomainUser | None:
        orm_obj = await self._get_by_condition_eq(DomainUser, OrmUser, OrmUser.email, email)
        return orm_obj


# For dependency injection
repository_user = Annotated[RepositoryUserSQL, Depends()]
