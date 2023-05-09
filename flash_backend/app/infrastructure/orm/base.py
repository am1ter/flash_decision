from datetime import datetime
from enum import Enum
from typing import Annotated, Self

from sqlalchemy import MetaData, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column, registry

from app.system.config import settings_db

# Custom `python types` to `database columns` mappings
int_pk = Annotated[int, mapped_column(primary_key=True)]
str_unq = Annotated[str, mapped_column(unique=True, index=True)]
datetime_current = Annotated[datetime, mapped_column(server_default=func.now())]


mapper_registry = registry()


@mapper_registry.mapped_as_dataclass
@as_declarative()
class Base:
    __name__: str
    metadata: MetaData

    # General columns
    id: Mapped[int_pk]
    datetime_create: Mapped[datetime_current]
    auto_columns = ["id", "datetime_create"]

    @declared_attr.directive
    def __tablename__(self) -> str:
        """Generate __tablename__ automatically"""
        return self.__name__.lower()

    @declared_attr.directive
    def __table_args__(self) -> dict:
        """Generate __table_args__ with infomation about database schema"""
        return {"schema": settings_db.DB_SCHEMA}

    @classmethod
    def create(cls, *args, **kwargs) -> Self:
        """Universal method to create new ORM objects"""

        # Allow to map domain model`s enums to orm`s columns
        for kw_name, kw_value in kwargs.items():
            if isinstance(kw_value, Enum):
                kwargs[kw_name] = kw_value.value

        # Allow server set some column value automatically
        for col in cls.auto_columns:
            kwargs[col] = None

        return cls(*args, **kwargs)
