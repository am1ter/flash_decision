from uuid import UUID

from sqlalchemy.orm.attributes import QueryableAttribute

from app.domain.repository import RepositoryUser
from app.domain.user import DomainUser, Email
from app.infrastructure.repositories.base import RepositorySqlAlchemy


class RepositoryUserSql(RepositorySqlAlchemy, RepositoryUser):
    async def get_by_id(self, _id: UUID) -> DomainUser:
        assert isinstance(DomainUser._id, QueryableAttribute)
        user = await self._select_one(DomainUser._id, _id)
        assert isinstance(user, DomainUser)
        return user

    async def get_by_email(self, email: str) -> DomainUser:
        assert isinstance(DomainUser.email, QueryableAttribute)
        user = await self._select_one(DomainUser.email, Email(email))
        assert isinstance(user, DomainUser)
        return user
