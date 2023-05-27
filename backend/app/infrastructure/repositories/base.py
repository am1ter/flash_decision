from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Sequence
from functools import wraps
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.dynamic import AppenderQuery

from app.domain.base import Entity
from app.infrastructure.db import db
from app.infrastructure.orm.mapper import init_orm_mappers
from app.infrastructure.repositories.identity_map import IdentityMapSQLAlchemy
from app.system.exceptions import DbConnectionError, DbObjectDuplicateError

# Run orm mappers as part of RepositorySQLAlchemy.
# Repository is the place where domain models and ORM models work together.
init_orm_mappers()


class Repository(ABC):
    """
    Abstract class for repositories - mediates between the domain and ORM.
    https://martinfowler.com/eaaCatalog/repository.html
    """

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
    It is an implementation of the `Repository` which use SQLAlchemy to connect to the db.
    This repository include identity maps as a storage (cache) for all data loaded from the db.
    Also it supports SQLAlchemy`s relationships.
    """

    def __init__(self, db: db) -> None:
        self._db = db
        self._identity_map = IdentityMapSQLAlchemy(db)

    @staticmethod
    def catch_db_errors(func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
        """Decorator to catch errors during requests to the database"""

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
    async def _select_one(self, col: InstrumentedAttribute, value: Any) -> Entity:
        """Return ONE database object using a `WHERE` condition"""

        # Try to find the query/entity in the related identity map; if not found, raise an exception
        try:
            entities = self._identity_map.queries.get_from_map(key=col, subkey=value)
        except KeyError:
            entities = await self._identity_map.queries.load_from_db(key=col, subkey=value)
        entity = entities[0]

        assert isinstance(entity, Entity)
        return entity

    @catch_db_errors
    async def _select_all(self, col: InstrumentedAttribute, value: Any) -> Sequence[Entity]:
        """Return ALL database objects using a `WHERE` condition"""

        # Try to find the query/entity in the related identity map; if not found, raise an exception
        try:
            entities = self._identity_map.queries.get_from_map(key=col, subkey=value)
        except KeyError:
            entities = await self._identity_map.queries.load_from_db(key=col, subkey=value)

        assert isinstance(entities, Sequence)
        return entities

    @catch_db_errors
    async def load_relationship(self, relationship: AppenderQuery) -> Sequence[Entity]:
        """Load lazy relationship using async session"""
        assert isinstance(relationship, AppenderQuery), f"{relationship=} is not a relationship"

        # Try to find the query/entity in the related identity map; if not found, raise an exception
        try:
            entities = self._identity_map.relationships.get_from_map(key=relationship)
        except KeyError:
            entities = await self._identity_map.relationships.load_from_db(key=relationship)

        assert isinstance(entities, Sequence)
        return entities

    def add(self, domain_obj: Entity) -> None:
        self._db.add(domain_obj)

    @catch_db_errors
    async def flush(self) -> None:
        await self._db.flush()

    @catch_db_errors
    async def refresh(self, domain_obj: Entity) -> None:
        await self._db.refresh(domain_obj)

    @catch_db_errors
    async def save(self) -> None:  # type: ignore[override]
        await self._db.commit()
