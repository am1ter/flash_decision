import dataclasses
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.domain.base import Entity
from app.infrastructure.db import db
from app.infrastructure.orm.base import Base


class Repository(ABC):
    """Abstract class for repositories"""

    @abstractmethod
    async def add(self, entity: Entity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Entity | None:
        raise NotImplementedError

    @abstractmethod
    async def save(self) -> None:
        raise NotImplementedError


class RepositorySQLAlchemy(Repository):
    """Parent `Repository` class implementation using SQLAlchemy as storage"""

    def __init__(self, db: db) -> None:
        self.db = db

    async def _get_by_condition(
        self,
        cls_domain: Entity,
        cls_orm: Base,
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
