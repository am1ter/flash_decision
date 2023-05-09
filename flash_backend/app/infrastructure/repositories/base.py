import dataclasses
from abc import ABC, abstractmethod
from typing import Any

import attrs
from sqlalchemy import select
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.domain.base import Entity
from app.infrastructure.db import db
from app.infrastructure.orm.base import Base


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

    cls_orm: type[Base]
    cls_domain: type[Entity]

    def __init__(self, db: db) -> None:
        self.db = db

    async def _get_by_condition_eq(
        self,
        cls_domain: type[Entity],
        cls_orm: type[Base],
        col: InstrumentedAttribute,
        value: Any,
    ) -> Entity | None:
        """Return db object using `WHERE` condition"""
        orm_obj = await self.db.scalar(select(cls_orm).where(col == value))
        try:
            domain_obj = cls_domain(**dataclasses.asdict(orm_obj))
        except TypeError:
            return None
        else:
            return domain_obj

    def add(self, domain_obj: Entity) -> None:
        orm_obj = self.__class__.cls_orm.create(**attrs.asdict(domain_obj))
        self.db.add(orm_obj)

    async def get_by_id(self, id: int) -> Entity | None:
        cls = self.__class__
        orm_obj = await self._get_by_condition_eq(cls.cls_domain, cls.cls_orm, cls.cls_orm.id, id)
        return orm_obj

    async def flush(self) -> None:
        await self.db.flush()

    async def save(self) -> None:
        await self.db.commit()
