from typing import Annotated

from fastapi import Depends

from app.domain.user import User as UserDomain
from app.infrastructure.orm.user import User as UserORM
from app.infrastructure.repositories.base import RepositorySQLAlchemy


class RepositoryUserSQL(RepositorySQLAlchemy):
    cls_domain = UserDomain
    cls_orm = UserORM

    async def get_by_email(self, email: str) -> UserDomain | None:
        orm_obj = await self._get_by_condition_eq(UserDomain, UserORM, UserORM.email, email)
        return orm_obj


# For dependency injection
repository_user = Annotated[RepositoryUserSQL, Depends()]
