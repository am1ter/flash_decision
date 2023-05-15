from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.domain.base import Entity
from app.infrastructure.db import db
from app.infrastructure.orm.mapper import init_orm_mappers

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

    async def _select_all(self, col: InstrumentedAttribute, value: Any) -> list[Entity]:
        """Return ALL db objects using `WHERE` condition"""
        objs = await self.db.scalars(select(col.parent).where(col == value))
        # AsyncSession requires to call unique() method on `uselist` quieres results
        return objs.unique().all()

    async def _select_one(self, col: InstrumentedAttribute, value: Any) -> Entity | None:
        """Return ONE db object using `WHERE` condition"""
        return await self.db.scalar(select(col.parent).where(col == value))

    def add(self, domain_obj: Entity) -> None:
        self.db.add(domain_obj)

    async def flush(self) -> None:
        await self.db.flush()

    async def refresh(self, domain_obj: Entity) -> None:
        await self.db.refresh(domain_obj)

    async def save(self) -> None:
        await self.db.commit()
