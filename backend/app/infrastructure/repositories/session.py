from uuid import UUID

from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm.dynamic import AppenderQuery

from app.domain.interfaces.repository import RepositorySession
from app.domain.session import Session
from app.domain.user import User
from app.infrastructure.repositories.base import RepositorySqlAlchemy


class RepositorySessionSql(RepositorySqlAlchemy, RepositorySession):
    async def get_by_id(self, _id: UUID) -> Session:
        assert isinstance(Session._id, QueryableAttribute)
        user = await self._select_one(Session._id, _id)
        assert isinstance(user, Session)
        return user

    async def get_all_sessions_by_user(self, user: User) -> list[Session]:
        assert isinstance(user.sessions, AppenderQuery)
        sessions: list[Session] = await self._load_from_db_relationship(user.sessions)
        return sessions
