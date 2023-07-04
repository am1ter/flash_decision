from app.domain.session import DomainSession
from app.infrastructure.repositories.base import RepositorySQLAlchemy


class RepositorySessionSQL(RepositorySQLAlchemy):
    async def get_by_id(self, id: int) -> DomainSession:
        user = await self._select_one(DomainSession.id, id)
        assert isinstance(user, DomainSession)
        return user
