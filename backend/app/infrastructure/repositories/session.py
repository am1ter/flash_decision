from app.domain.session import DomainSession
from app.infrastructure.repositories.base import RepositorySqlAlchemy


class RepositorySessionSql(RepositorySqlAlchemy):
    async def get_by_id(self, _id: str) -> DomainSession:
        user = await self._select_one(DomainSession._id, _id)
        assert isinstance(user, DomainSession)
        return user
