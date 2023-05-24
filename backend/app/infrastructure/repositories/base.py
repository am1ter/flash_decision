from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.dynamic import AppenderQuery

from app.domain.base import Entity
from app.infrastructure.db import db
from app.infrastructure.orm.mapper import init_orm_mappers
from app.system.exceptions import DbObjectNotFoundError

# Run orm mappers as the part of RepositorySQLAlchemy
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

    async def _select_all(self, col: Any, value: Any) -> Sequence[Entity]:
        """Return ALL db objects using `WHERE` condition"""
        assert isinstance(col, InstrumentedAttribute), f"{col=} is not a valid db column"
        objs_db = await self.db.scalars(select(col.parent).where(col == value))
        # AsyncSession requires to call unique() method on `uselist` quieres results
        objs = objs_db.unique().all()
        if not objs:
            raise DbObjectNotFoundError
        return objs

    async def _select_one(self, col: Any, value: Any) -> Entity:
        """Return ONE db object using `WHERE` condition"""
        assert isinstance(col, InstrumentedAttribute), f"{col=} is not a valid db column"
        entity = await self.db.scalar(select(col.parent).where(col == value))
        if not entity:
            raise DbObjectNotFoundError
        return entity

    async def load_relationship(self, relationship: Any) -> list[Entity]:
        """Load lazy relationship using async session"""
        assert isinstance(relationship, AppenderQuery), f"{relationship=} is not a relationship"
        query = await self.db.execute(relationship)
        # All() method returns list of tuples with a single object inside every tuple
        return [obj[0] for obj in query.all()]

    def add(self, domain_obj: Entity) -> None:
        self.db.add(domain_obj)

    async def flush(self) -> None:
        await self.db.flush()

    async def refresh(self, domain_obj: Entity) -> None:
        await self.db.refresh(domain_obj)

    async def save(self) -> None:
        await self.db.commit()
