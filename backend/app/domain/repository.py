from abc import ABCMeta, abstractmethod
from decimal import Decimal
from uuid import UUID

from app.domain.base import Entity
from app.domain.scoreboard import ScoreboardRecord, ScoreboardRecords
from app.domain.session import Session
from app.domain.session_iteration import Iteration, IterationCollection
from app.domain.session_result import SessionResult
from app.domain.user import User
from app.system.constants import SessionMode


class Repository(metaclass=ABCMeta):
    """
    Abstract class for repositories - mediates between the domain and ORM.
    Repository is the place where domain models and ORM models work together.
    https://martinfowler.com/eaaCatalog/repository.html
    """

    @abstractmethod
    def add(self, entity: Entity) -> None:
        """Add an entity to the repository"""


class RepositoryUser(Repository, metaclass=ABCMeta):
    @abstractmethod
    async def get_by_id(self, _id: UUID) -> User:
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User:
        ...


class RepositorySession(Repository, metaclass=ABCMeta):
    @abstractmethod
    async def get_by_id(self, _id: UUID) -> Session:
        ...

    @abstractmethod
    async def get_all_sessions_by_user(self, user: User) -> list[Session]:
        ...


class RepositoryIteration(Repository, metaclass=ABCMeta):
    @abstractmethod
    def get_iteration_collection(self, session_id: UUID) -> IterationCollection:
        ...

    @abstractmethod
    def get_iteration(self, session_id: UUID, iteration_num: int) -> Iteration:
        ...


class RepositoryScoreboard(Repository, metaclass=ABCMeta):
    @abstractmethod
    def update_score(self, session_result: SessionResult) -> Decimal:
        ...

    @abstractmethod
    def get_full_scoreboard(self, mode: SessionMode) -> ScoreboardRecords:
        ...

    @abstractmethod
    def get_scoreboard_record(self, user: User, mode: SessionMode) -> ScoreboardRecord:
        ...
