from abc import ABC, abstractmethod
from collections import defaultdict
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
# Repository is the place where domain models and orm models work together.
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
    In each child class, the attributes `cls_orm` and `cls_domain` must be defined.
    """

    def __init__(self, db: db) -> None:
        self.db = db
        self._identity_map_query: dict[InstrumentedAttribute, dict[Any, Entity | Sequence[Entity]]]
        self._identity_map_query = defaultdict(dict)
        self._identity_map_relationship: dict[Entity, dict[str, Entity | Sequence[Entity]]]
        self._identity_map_relationship = defaultdict(dict)
        self._identity_map_entity: dict[type[Entity], dict[int, Entity]]
        self._identity_map_entity = defaultdict(dict)

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
    async def _select_all(self, col: InstrumentedAttribute, value: Any) -> Sequence[Entity]:
        """Return ALL database objects using `WHERE` condition"""
        assert isinstance(col, InstrumentedAttribute), f"{col=} is not a valid database column"

        # Try to extract objects from the identity map; if not found, query the database
        try:
            entities = self._identity_map_query[col][value]
        except KeyError:
            entities_db = await self.db.scalars(select(col.parent).where(col == value))
            # AsyncSession requires to call unique() method on `uselist` quieres results
            entities = entities_db.unique().all()
            if not entities:
                raise DbObjectNotFoundError  # noqa: B904
            # Save query and its results to the identity maps
            self._identity_map_query[col][value] = entities
            for entity in entities:
                self._identity_map_entity[type(entity)][entity.id] = entity
        else:
            # If from identity map was extracted single Entity convert it to list
            if not isinstance(entities, Sequence):
                entities = [entities]

        return entities

    async def _select_one_by_id(self, col: InstrumentedAttribute, value: Any) -> Entity:
        """Return ONE database object by its `id` column"""
        try:
            entity = self._identity_map_entity[col.parent.class_][value]
        except KeyError:
            entity_db = await self.db.scalar(select(col.parent).where(col == value))
            if not entity_db:
                raise DbObjectNotFoundError  # noqa: B904
            entity = entity_db
            # Save query results to the identity map
            self._identity_map_entity[type(entity)][entity.id] = entity

        return entity

    @catch_db_errors
    async def _select_one(self, col: InstrumentedAttribute, value: Any) -> Entity:
        """Return ONE database object using `WHERE` condition"""
        assert isinstance(col, InstrumentedAttribute), f"{col=} is not a valid database column"

        # For selecting by id, use another method
        if col.name == "id":
            return await self._select_one_by_id(col, value)

        # Try to extract object from the identity map; if not found, query the database
        try:
            entity = self._identity_map_query[col][value]
        except KeyError:
            entity_db: Entity | None = await self.db.scalar(select(col.parent).where(col == value))
            if not entity_db:
                raise DbObjectNotFoundError  # noqa: B904
            entity = entity_db
            # Save query and its results to the identity maps
            self._identity_map_query[col][value] = entity
            self._identity_map_entity[type(entity)][entity.id] = entity
        else:
            # If from identity map was extracted list of entities return only first
            if isinstance(entity, Sequence) and len(entity):
                entity = entity[0]

        assert isinstance(entity, Entity), f"{entity} is not an Entity"
        return entity

    @catch_db_errors
    async def load_relationship(self, relationship: AppenderQuery) -> Sequence[Entity]:
        """Load lazy relationship using async session"""
        assert isinstance(relationship, AppenderQuery), f"{relationship=} is not a relationship"

        # Try to extract object from identity map, if not found ask db
        obj_from = relationship.instance
        obj_attr = relationship.attr.key
        try:
            entities = self._identity_map_relationship[obj_from][obj_attr]
        except KeyError:
            query = await self.db.execute(relationship)
            # All() method returns list of tuples with a single object inside every tuple
            entities = [obj[0] for obj in query.unique().all()]
            # Save query and its results to the identity maps
            self._identity_map_relationship[obj_from][obj_attr] = entities
            for entity in entities:
                self._identity_map_entity[type(entity)][entity.id] = entity

        # Lazy relationships always must be a list (it cannot be used with one-to-one relationships)
        if not isinstance(entities, Sequence):
            entities = [entities]

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
