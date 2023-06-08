from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Sequence
from functools import wraps
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.dynamic import AppenderQuery

from app.domain.base import Entity
from app.infrastructure.repositories.identity_map import IdentityMapSQLAlchemy
from app.system.exceptions import (
    DbConnectionError,
    DbObjectCannotBeCreatedError,
    DbObjectNotFoundError,
)


class Repository(ABC):
    """
    Abstract class for repositories - mediates between the domain and ORM.
    Repository is the place where domain models and ORM models work together.
    https://martinfowler.com/eaaCatalog/repository.html
    """

    @abstractmethod
    def add(self, entity: Entity) -> None:
        """Add an entity to the repository"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Entity | None:
        """Retrieve an entity from the repository by its ID"""
        raise NotImplementedError


class RepositorySQLAlchemy(Repository):
    """
    Implementation of the `Repository` which uses SQLAlchemy to connect to self._db.
    This repository includes identity maps as a storage (cache) for all data loaded from self._db.
    It also supports SQLAlchemy's relationships.
    """

    def __init__(
        self, db: AsyncSession, identity_map: IdentityMapSQLAlchemy = IdentityMapSQLAlchemy()
    ) -> None:
        self._db = db
        self._identity_map = identity_map

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
                raise DbObjectCannotBeCreatedError from e
            return result

        return inner

    async def _load_from_db_query(
        self, col: InstrumentedAttribute, val: Any, *, uselist: bool
    ) -> Sequence[Entity]:
        """Load ONE/ALL entities from the database using `WHERE` condition by column and a value"""

        if uselist:
            query = await self._db.scalars(select(col.parent).where(col == val))
            entities = query.unique().all()
        else:
            entity = await self._db.scalar(select(col.parent).where(col == val))
            entities = [entity] if entity else []  # Use single type for all return variants
        if not entities:  # If entities are not found in the database, raise an exception
            raise DbObjectNotFoundError
        self._identity_map.queries.add(col, val, entities)
        return entities

    async def _load_from_db_relationship(self, relationship: AppenderQuery) -> Sequence[Entity]:
        """Load entities from the database using a SQLAlchemy's relationship"""

        query = await self._db.execute(relationship)
        entities = [obj[0] for obj in query.unique().all()]  # obj is tuple with only one element
        if not entities:  # If entities are not found in the database, raise an exception
            raise DbObjectNotFoundError
        self._identity_map.relationships.add(relationship, entities)
        return entities

    @catch_db_errors
    async def _select_one(self, col: InstrumentedAttribute, val: Any) -> Entity:
        """Return a single object from the identity map or the database"""

        try:  # Try to find the query/entity in the related identity map
            entities = self._identity_map.queries.get(col, val)
        except KeyError:  # If not found, load it from the database
            entities = await self._load_from_db_query(col, val, uselist=False)
        entity = entities[0]

        assert isinstance(entity, Entity)
        return entity

    @catch_db_errors
    async def _select_all(self, col: InstrumentedAttribute, val: Any) -> Sequence[Entity]:
        """Return all objects from the identity map or the database"""

        try:  # Try to find the query/entity in the related identity map
            entities = self._identity_map.queries.get(col, val)
        except KeyError:  # If not found, load them from the database
            entities = await self._load_from_db_query(col, val, uselist=True)

        assert isinstance(entities, Sequence)
        return entities

    @catch_db_errors
    async def load_relationship(self, relationship: AppenderQuery) -> Sequence[Entity]:
        """Load a lazy relationship using the identity map or the database"""

        assert isinstance(relationship, AppenderQuery), f"{relationship=} is not a relationship"

        try:  # Try to find the query/entity in the related identity map
            entities = self._identity_map.relationships.get(relationship)
        except KeyError:  # If not found, load it from the database
            entities = await self._load_from_db_relationship(relationship)

        assert isinstance(entities, Sequence)
        return entities

    def add(self, domain_obj: Entity) -> None:
        """Add an entity to the repository"""
        self._db.add(domain_obj)

    @catch_db_errors
    async def flush(self) -> None:
        """Flush pending changes to the database"""
        await self._db.flush()

    @catch_db_errors
    async def refresh(self, domain_obj: Entity) -> None:
        """Refresh the state of an entity with the database"""
        await self._db.refresh(domain_obj)
