from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Sequence
from functools import wraps
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.dynamic import AppenderQuery

from app.domain.base import Entity
from app.infrastructure.db import db
from app.infrastructure.orm.mapper import init_orm_mappers
from app.system.exceptions import DbConnectionError, DbObjectDuplicateError, DbObjectNotFoundError

# Run orm mappers as the part of RepositorySQLAlchemy.
# Repository is the place where domain models and orm models works together.
init_orm_mappers()


class Repository(ABC):
    """Abstract class for repositories"""

    @abstractmethod
    def add(self, entity: Entity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Entity | None:
        raise NotImplementedError

    @abstractmethod
    async def save(self) -> None:
        raise NotImplementedError


class RepositorySQLAlchemy(Repository):
    """
    Parent `Repository` class implementation using SQLAlchemy as storage.
    In each children class must be defined attributes `cls_orm` and `cls_domain`.
    """

    def __init__(self, db: db) -> None:
        self.db = db

    @staticmethod
    def catch_db_errors(func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
        """Decorator to catch errors during request to the db"""

        @wraps(func)
        async def inner(*args, **kwargs) -> Any:
            try:
                result = await func(*args, **kwargs)
            except ConnectionRefusedError as e:
                raise DbConnectionError from e
            except IntegrityError as e:
                raise DbObjectDuplicateError from e
            return result

        return inner

    @catch_db_errors
    async def _select_all(self, col: Any, value: Any) -> Sequence[Entity]:
        """Return ALL db objects using `WHERE` condition"""
        assert isinstance(col, InstrumentedAttribute), f"{col=} is not a valid db column"
        objs_db = await self.db.scalars(select(col.parent).where(col == value))
        # AsyncSession requires to call unique() method on `uselist` quieres results
        entities = objs_db.unique().all()
        if not entities:
            raise DbObjectNotFoundError
        return entities

    @catch_db_errors
    async def _select_one(self, col: Any, value: Any) -> Entity:
        """Return ONE db object using `WHERE` condition"""
        assert isinstance(col, InstrumentedAttribute), f"{col=} is not a valid db column"
        entity = await self.db.scalar(select(col.parent).where(col == value))
        if not entity:
            raise DbObjectNotFoundError
        return entity

    @catch_db_errors
    async def load_relationship(self, relationship: Any) -> list[Entity]:
        """Load lazy relationship using async session"""
        assert isinstance(relationship, AppenderQuery), f"{relationship=} is not a relationship"
        query = await self.db.execute(relationship)
        # All() method returns list of tuples with a single object inside every tuple
        entities = [obj[0] for obj in query.all()]
        return entities

    def add(self, domain_obj: Entity) -> None:
        self.db.add(domain_obj)

    @catch_db_errors
    async def flush(self) -> None:
        await self.db.flush()

    @catch_db_errors
    async def refresh(self, domain_obj: Entity) -> None:
        await self.db.refresh(domain_obj)

    @catch_db_errors
    async def save(self) -> None:  # type: ignore[override]
        await self.db.commit()
