from uuid6 import UUID

from app.domain.session import DomainSession
from app.infrastructure.repositories.base import RepositorySqlAlchemy


class RepositorySessionSql(RepositorySqlAlchemy):
    async def get_by_id(self, _id: UUID) -> DomainSession:
        user = await self._select_one(DomainSession._id, _id)
        assert isinstance(user, DomainSession)
        return user
