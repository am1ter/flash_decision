from uuid6 import UUID

from app.domain.user import DomainUser, Email
from app.infrastructure.repositories.base import RepositorySqlAlchemy


class RepositoryUserSql(RepositorySqlAlchemy):
    async def get_by_id(self, _id: UUID) -> DomainUser:
        user = await self._select_one(DomainUser._id, _id)
        assert isinstance(user, DomainUser)
        return user

    async def get_by_email(self, email: str) -> DomainUser:
        user = await self._select_one(DomainUser.email, Email(email))
        assert isinstance(user, DomainUser)
        return user
