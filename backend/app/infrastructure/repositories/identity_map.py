from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.domain.base import Entity
from app.system.exceptions import DbObjectNotFoundError


class IdentityMapSQLAlchemyABC(ABC):
    """
    Ensures that each object gets loaded only once by keeping every loaded object in a map.
    Looks up objects using the map when referring to them and if not found query the database.
    In fact, it works as local cache for SQLAlchemy repositories.
    https://martinfowler.com/eaaCatalog/identityMap.html
    """

    def __init__(self, identity_map: "IdentityMapSQLAlchemy") -> None:
        self._identity_map = identity_map
        self.map: dict = defaultdict(dict)

    @abstractmethod
    def add_to_map(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_from_map(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def load_from_db(self, *args, **kwargs) -> Entity | Sequence[Entity]:
        raise NotImplementedError


class IdentityMapSQLAlchemyQueries(IdentityMapSQLAlchemyABC):
    """Cache SQL queries and their results"""

    map: dict[InstrumentedAttribute, dict[Any, Sequence[Entity]]]

    def add_to_map(self, key: Any, subkey: Any, entities: Sequence[Entity]) -> None:
        self.map[key][subkey] = entities
        for entity in entities:
            self._identity_map.entities.add_to_map(entity)

    def get_from_map(self, key: Any, subkey: Any) -> Sequence[Entity]:
        # For selecting by id, firstly try to find in entity identity map
        if key.name == "id":
            entity = self._identity_map.entities.get_from_map(cls_type=key.parent.class_, id=subkey)
            return [entity]
        # Try to find in the identity map with queries
        entities = self.map[key][subkey]
        return entities

    async def load_from_db(self, key: Any, subkey: Any) -> Sequence[Entity]:
        query = await self._identity_map._db.scalars(select(key.parent).where(key == subkey))
        entities = query.unique().all()
        # If entities are not found in the database, raise an exception
        if not entities:
            raise DbObjectNotFoundError
        self.add_to_map(key, subkey, entities)
        return entities


class IdentityMapSQLAlchemyRelationships(IdentityMapSQLAlchemyABC):
    """Cache entities loaded via ORM relationships"""

    map: dict[Entity, dict[str, Sequence[Entity]]]

    def add_to_map(self, key: Any, entities: Sequence[Entity]) -> None:
        obj_from, relationship_attr_name = key.instance, key.attr.key  # i.e.: DomainUser, auths
        self.map[obj_from][relationship_attr_name] = entities
        for entity in entities:
            self._identity_map.entities.add_to_map(entity)

    def get_from_map(self, key: Any) -> Sequence[Entity]:
        entities = self.map[key.instance][key.attr.key]
        return entities

    async def load_from_db(self, key: Any) -> Sequence[Entity]:
        query = await self._identity_map._db.execute(key)
        entities = [obj[0] for obj in query.unique().all()]
        # If entities are not found in the database, raise an exception
        if not entities:
            raise DbObjectNotFoundError
        self.add_to_map(key, entities)
        return entities


class IdentityMapSQLAlchemyEntities(IdentityMapSQLAlchemyABC):
    """Store every domain object loaded from db using its type and id"""

    map: dict[type, dict[int, Entity]]

    def add_to_map(self, entity: Entity) -> None:
        self.map[type(entity)][entity.id] = entity

    def get_from_map(self, cls_type: type, id: int) -> Entity:
        return self.map[cls_type][id]

    async def load_from_db(self, key: Any, subkey: Any) -> Entity:
        entity = await self._identity_map._db.scalar(select(key.parent).where(key == subkey))
        # If the entity is not found in the database, raise an exception
        if not entity:
            raise DbObjectNotFoundError
        self.add_to_map(entity)
        return entity


class IdentityMapSQLAlchemy:
    """Collection of 3 identity maps for SQLAlchemy"""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self.queries = IdentityMapSQLAlchemyQueries(self)
        self.relationships = IdentityMapSQLAlchemyRelationships(self)
        self.entities = IdentityMapSQLAlchemyEntities(self)
