from collections.abc import Awaitable, Callable, Sequence
from functools import wraps
from typing import Any, TypeVar, cast
from uuid import UUID

import bson
from attrs import asdict
from pymongo.errors import ConnectionFailure
from sqlalchemy import select
from sqlalchemy.exc import InterfaceError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm.dynamic import AppenderQuery

from app.domain.base import Entity, custom_serializer
from app.domain.repository import Repository
from app.infrastructure.databases.nosql import DbNoSql
from app.infrastructure.repositories.identity_map import IdentityMapSqlAlchemy
from app.system.exceptions import DbConnectionError, DbObjectNotFoundError

DecoratedFunction = TypeVar("DecoratedFunction", bound=Callable)
DecoratedFunctionAwaitable = TypeVar("DecoratedFunctionAwaitable", bound=Callable[..., Awaitable])


class RepositorySqlAlchemy(Repository):
    """
    Implementation of the `Repository` which uses SQLAlchemy to connect to self._db.
    This repository includes identity maps as a storage (cache) for all data loaded from self._db.
    It also supports SQLAlchemy's relationships.
    """

    def __init__(
        self, db: AsyncSession, identity_map: type[IdentityMapSqlAlchemy] = IdentityMapSqlAlchemy
    ) -> None:
        self._db = db
        self._identity_map = identity_map()

    @staticmethod
    def catch_db_errors(func: DecoratedFunctionAwaitable) -> DecoratedFunctionAwaitable:
        """Decorator to catch errors during requests to the database"""

        @wraps(func)
        async def inner(*args, **kwargs) -> Any:
            try:
                result = await func(*args, **kwargs)
            except (ConnectionRefusedError, InterfaceError) as e:
                raise DbConnectionError from e
            return result

        return cast(DecoratedFunctionAwaitable, inner)

    async def _load_from_db_query(
        self, col: QueryableAttribute, val: Any, *, uselist: bool
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

        query = await self._db.scalars(relationship.statement)
        entities = query.unique().all()
        if not entities:  # If entities are not found in the database, raise an exception
            raise DbObjectNotFoundError
        self._identity_map.relationships.add(relationship, entities)
        return entities

    @catch_db_errors
    async def _select_one(self, col: QueryableAttribute, val: Any) -> Entity:
        """Return a single object from the identity map or the database"""

        try:  # Try to find the query/entity in the related identity map
            entities = self._identity_map.queries.get(col, val)
        except KeyError:  # If not found, load it from the database
            entities = await self._load_from_db_query(col, val, uselist=False)
        entity = entities[0]

        assert isinstance(entity, Entity)
        return entity

    @catch_db_errors
    async def _select_all(self, col: QueryableAttribute, val: Any) -> Sequence[Entity]:
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


class RepositoryNoSqlMongo(Repository):
    def __init__(self, db: DbNoSql) -> None:
        self._db = db.engine

    @staticmethod
    def catch_db_errors(func: DecoratedFunction) -> DecoratedFunction:
        """Decorator to catch errors during requests to the database"""

        @wraps(func)
        def inner(*args, **kwargs) -> Any:
            try:
                result = func(*args, **kwargs)
            except ConnectionFailure as e:
                raise DbConnectionError from e
            return result

        return cast(DecoratedFunction, inner)

    def _convert_uuid_to_binary(self, field: dict) -> dict:
        """Convert all UUID values into binary format"""
        for key, val in field.items():
            if isinstance(val, UUID):
                field[key] = bson.Binary.from_uuid(val)
        return field

    def _convert_binary_to_uuid(self, doc: dict) -> dict:
        """Convert binary formated values into pythonic format"""
        for key, val in doc.items():
            if isinstance(val, bson.Binary):
                doc[key] = UUID(bytes=bson.BSON(val))
        return doc

    @catch_db_errors
    def add(self, entity: Entity) -> None:
        """Serialize and save an entity to the database"""
        entity_as_dict = asdict(entity, recurse=True, value_serializer=custom_serializer)
        entity_as_dict = self._convert_uuid_to_binary(entity_as_dict)
        collection_name = entity.__class__.__name__
        self._db[collection_name].insert_one(entity_as_dict)

    @catch_db_errors
    def _select_one(self, entity_class: type, field: dict) -> dict:
        """Extract one record from the database"""
        collection_name = entity_class.__name__
        field_updated = self._convert_uuid_to_binary(field)
        obj_from_db = self._db[collection_name].find_one(field_updated)
        if not obj_from_db:  # If object are not found in the database, raise an exception
            raise DbObjectNotFoundError
        return obj_from_db

    @catch_db_errors
    def _select_all(self, entity_class: type, field: dict) -> list[dict]:
        """Extract all related records from the database"""
        collection_name = entity_class.__name__
        all_documents = []
        field_updated = self._convert_uuid_to_binary(field)
        documents_from_db = self._db[collection_name].find(field_updated)
        for doc in documents_from_db:
            all_documents.append(doc)
        if not all_documents:  # If objects are not found in the database, raise an exception
            raise DbObjectNotFoundError
        return all_documents
