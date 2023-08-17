from uuid import UUID

from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm.dynamic import AppenderQuery

from app.domain.repository import RepositorySession
from app.domain.session import DomainSession
from app.domain.user import DomainUser
from app.infrastructure.repositories.base import RepositorySqlAlchemy


class RepositorySessionSql(RepositorySqlAlchemy, RepositorySession):
    async def get_by_id(self, _id: UUID) -> DomainSession:
        assert isinstance(DomainSession._id, QueryableAttribute)
        user = await self._select_one(DomainSession._id, _id)
        assert isinstance(user, DomainSession)
        return user

    async def get_all_sessions_by_user(self, user: DomainUser) -> list[DomainSession]:
        assert isinstance(user.sessions, AppenderQuery)
        sessions: list[DomainSession] = await self._load_from_db_relationship(user.sessions)
        return sessions
