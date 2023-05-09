from typing import Annotated

import attrs
from fastapi import Depends

from app.domain.user import User as UserDomain
from app.infrastructure.orm.user import User as UserORM
from app.infrastructure.repositories.base import RepositorySQLAlchemy


class RepositoryUserSQL(RepositorySQLAlchemy):
    def add(self, domain_obj: UserDomain) -> None:
        orm_obj = UserORM.create(**attrs.asdict(domain_obj))
        self.db.add(orm_obj)

    async def get_by_id(self, id: int) -> UserDomain | None:
        orm_obj = await self._get_by_condition(UserDomain, UserORM, UserORM.id, id)
        return orm_obj

    async def get_by_email(self, email: str) -> UserDomain | None:
        orm_obj = await self._get_by_condition(UserDomain, UserORM, UserORM.email, email)
        return orm_obj

    async def flush(self) -> None:
        await self.db.flush()

    async def save(self) -> None:
        await self.db.commit()


# For dependency injection
repository_user = Annotated[RepositoryUserSQL, Depends()]
