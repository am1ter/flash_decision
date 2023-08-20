from abc import ABCMeta, abstractmethod
from collections import defaultdict
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm.dynamic import AppenderQuery

from app.domain.interfaces.domain import Entity


class IdentityMapSqlAlchemyABC(metaclass=ABCMeta):
    """
    Abstract base class for SQLAlchemy Identity Map.
    Ensures that each object gets loaded only once by keeping every loaded object in a map.
    Looks up objects using the map when referring to them and if not found, query the database.
    In fact, it works as a local cache for SQLAlchemy repositories.
    https://martinfowler.com/eaaCatalog/identityMap.html
    """

    def __init__(self, identity_map: "IdentityMapSqlAlchemy") -> None:
        self._identity_map = identity_map
        self._map: dict = defaultdict(dict)

    @abstractmethod
    def add(self, *args, **kwargs) -> None:
        """Add entities or query parameters to the identity map"""
        raise NotImplementedError

    @abstractmethod
    def get(self, *args, **kwargs) -> Sequence[Entity] | Entity:
        """Retrieve entities or query results from the identity map"""
        raise NotImplementedError


class IdentityMapSqlAlchemyQueries(IdentityMapSqlAlchemyABC):
    """Cache SQL queries and their results"""

    _map: dict[QueryableAttribute, dict[Any, Sequence[Entity]]]

    def add(self, col: QueryableAttribute, val: Any, entities: Sequence[Entity]) -> None:
        """Add query parameters to its identity map and also add all entities to a separate map."""
        self._map[col][val] = entities
        for entity in entities:
            self._identity_map.entities.add(entity)

    def get(self, col: QueryableAttribute, val: Any) -> Sequence[Entity]:
        """Find the entities in the local storage by query parameters"""
        # For selecting by ID, use the entity identity map instead
        if col.key == "_id":
            entity = self._identity_map.entities.get(cls_type=col.parent.class_, _id=val)
            return [entity]
        # Try to find in the identity map with queries
        entities = self._map[col][val]
        return entities


class IdentityMapSqlAlchemyRelationships(IdentityMapSqlAlchemyABC):
    """Cache entities loaded via ORM relationships."""

    _map: dict[Entity, dict[str, Sequence[Entity]]]

    def add(self, relationship: AppenderQuery, entities: Sequence[Entity]) -> None:
        """Add the relationship to its identity map and also add all entities to a separate map."""
        self._map[relationship.instance][relationship.attr.key] = entities
        for entity in entities:
            self._identity_map.entities.add(entity)

    def get(self, relationship: AppenderQuery) -> Sequence[Entity]:
        """Find the entities in the local storage by relationship."""
        entities = self._map[relationship.instance][relationship.attr.key]
        return entities


class IdentityMapSqlAlchemyEntities(IdentityMapSqlAlchemyABC):
    """Store every domain object loaded from the database using its type and ID."""

    _map: dict[type, dict[UUID, Entity]]

    def add(self, entity: Entity) -> None:
        """Add an entity to its identity map."""
        self._map[type(entity)][entity._id] = entity

    def get(self, cls_type: type, _id: UUID) -> Entity:
        """Find the entity in the local storage by type and ID."""
        entity = self._map[cls_type][_id]
        return entity


class IdentityMapSqlAlchemy:
    """Collection of 3 identity maps for SQLAlchemy."""

    def __init__(self) -> None:
        self.queries = IdentityMapSqlAlchemyQueries(self)
        self.relationships = IdentityMapSqlAlchemyRelationships(self)
        self.entities = IdentityMapSqlAlchemyEntities(self)
