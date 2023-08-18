from uuid import UUID

from sqlalchemy.orm.attributes import QueryableAttribute

from app.domain.repository import RepositoryUser
from app.domain.user import Email, User
from app.infrastructure.repositories.base import RepositorySqlAlchemy


class RepositoryUserSql(RepositorySqlAlchemy, RepositoryUser):
    async def get_by_id(self, _id: UUID) -> User:
        assert isinstance(User._id, QueryableAttribute)
        user = await self._select_one(User._id, _id)
        assert isinstance(user, User)
        return user

    async def get_by_email(self, email: str) -> User:
        assert isinstance(User.email, QueryableAttribute)
        user = await self._select_one(User.email, Email(email))
        assert isinstance(user, User)
        return user
