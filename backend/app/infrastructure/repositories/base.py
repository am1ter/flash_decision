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

    async def _select_one_by_id(self, col: InstrumentedAttribute, value: Any) -> Entity:
        """Return ONE database object by its `id` column"""
        entity = await self._get_from_identity_map(self._select_one_by_id, col, value)
        assert isinstance(entity, Entity)
        return entity

    async def _select_one(self, col: InstrumentedAttribute, value: Any) -> Entity:
        """Return ONE database object using `WHERE` condition"""
        # For selecting by id, use another method
        if col.name == "id":
            return await self._select_one_by_id(col, value)
        entity = await self._get_from_identity_map(self._select_one, col, value)
        assert isinstance(entity, Entity)
        return entity

    async def _select_all(self, col: InstrumentedAttribute, value: Any) -> Sequence[Entity]:
        """Return ALL database objects using `WHERE` condition"""
        entities = await self._get_from_identity_map(self._select_all, col, value)
        assert isinstance(entities, Sequence)
        return entities

    async def load_relationship(self, relationship: AppenderQuery) -> Sequence[Entity]:
        """Load lazy relationship using async session"""
        assert isinstance(relationship, AppenderQuery), f"{relationship=} is not a relationship"
        col = relationship.instance
        entities = await self._get_from_identity_map(self.load_relationship, col, relationship)
        assert isinstance(entities, Sequence)
        return entities

    @catch_db_errors
    async def _get_from_identity_map(
        self, func: Callable, col: InstrumentedAttribute | type[Entity] | Entity, value: Any
    ) -> Sequence[Entity] | Entity:
        match func:
            case self._select_one:
                assert isinstance(col, InstrumentedAttribute)
                m = {
                    "identity_map": self._identity_map_query[col],
                    "identity_map_value": value,
                    "sql_query": self.db.scalar(select(col.parent).where(col == value)),
                    "sql_query_processing": lambda query: query,
                }
            case self._select_one_by_id:
                assert isinstance(col, InstrumentedAttribute)
                m = {
                    "identity_map": self._identity_map_entity[col.parent.class_],
                    "identity_map_value": value,
                    "sql_query": self.db.scalar(select(col.parent).where(col == value)),
                    "sql_query_processing": lambda query: query,
                }
            case self._select_all:
                assert isinstance(col, InstrumentedAttribute)
                m = {
                    "identity_map": self._identity_map_query[col],
                    "identity_map_value": value,
                    "sql_query": self.db.scalars(select(col.parent).where(col == value)),
                    "sql_query_processing": lambda query: query.unique().all(),
                }
            case self.load_relationship:
                assert isinstance(col, Entity)
                m = {
                    "identity_map": self._identity_map_relationship[col],
                    "identity_map_value": value.attr.key,
                    "sql_query": self.db.execute(value),
                    "sql_query_processing": lambda query: [obj[0] for obj in query.unique().all()],
                }

        # Logic of the loading process
        # Try to find query/entity in the related identity map
        try:
            entities: Sequence[Entity] | Entity = m["identity_map"][m["identity_map_value"]]
        except KeyError:
            # If not found run SQL query and convert db records to entities
            query = await m["sql_query"]
            entities = m["sql_query_processing"](query)

            # If enities not found in the database, raise exception
            if not entities:
                raise DbObjectNotFoundError  # noqa: B904

            # Save query to the related identity map
            m["identity_map"][m["identity_map_value"]] = entities

            # Save entities from the query to the identity map with entities
            entities_as_list = entities if isinstance(entities, Sequence) else [entities]
            for entity in entities_as_list:
                self._identity_map_entity[type(entity)][entity.id] = entity
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
