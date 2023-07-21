import contextlib
from datetime import datetime
from enum import Enum as EnumStd
from typing import Annotated, Any

from sqlalchemy import Enum, MetaData, Table, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapper, as_declarative, declared_attr, mapped_column, registry

from app.system.config import Settings

# Custom `python types` to `database columns` mappings
uuid_pk = Annotated[str, mapped_column(UUID, primary_key=True)]
str_unq = Annotated[str, mapped_column(unique=True, index=True)]
datetime_current = Annotated[datetime, mapped_column(server_default=func.now())]
jsonb = Annotated[dict[str, Any], mapped_column(JSONB)]


def mapped_column_enum(enum_class: type[EnumStd], default: EnumStd | None = None) -> Any:
    return mapped_column(
        Enum(enum_class, name=enum_class.__name__, schema=Settings().sql.SQL_SCHEMA),
        nullable=False,
        default=default.value if default else None,
    )


mapper_registry = registry()


@mapper_registry.mapped_as_dataclass
@as_declarative()
class Base:
    """Declarative approach used only as alternative way to define database tables"""

    __name__: str
    __table__: Table  # Automatically generated during initialization; used for mappings
    __mapper__: Mapper
    metadata: MetaData

    @declared_attr.directive
    def __tablename__(self) -> str:
        """
        Generate __tablename__ automatically using class name.
        Remove `ORM` prefix from it.
        For inherited ORM classes (polymorphic) use parents tablename.
        """
        with contextlib.suppress(AssertionError):
            assert hasattr(self.__class__, "__mapper_args__")
            if "polymorphic_identity" in self.__class__.__mapper_args__:
                return self.__mapper__.mapped_table.name
        orm_class_name_prefix = "orm"
        cls_name = self.__name__.lower()
        if cls_name[: len(orm_class_name_prefix)] == orm_class_name_prefix:
            return cls_name[len(orm_class_name_prefix) :]
        else:
            return cls_name

    @declared_attr.directive
    def __table_args__(self) -> dict:
        """Generate __table_args__ with infomation about database schema"""
        return {"schema": Settings().sql.SQL_SCHEMA}
