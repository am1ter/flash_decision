from datetime import datetime
from enum import Enum as EnumStd
from typing import Annotated, Any

from sqlalchemy import Enum, MetaData, Table, func
from sqlalchemy.orm import as_declarative, declared_attr, mapped_column, registry

from app.system.config import settings_db

# Custom `python types` to `database columns` mappings
int_pk = Annotated[int, mapped_column(primary_key=True)]
str_unq = Annotated[str, mapped_column(unique=True, index=True)]
datetime_current = Annotated[datetime, mapped_column(server_default=func.now())]


def mapped_column_enum(enum_class: type[EnumStd], default: EnumStd | None = None) -> Any:
    return mapped_column(
        Enum(enum_class, name=enum_class.__name__, schema=settings_db.DB_SCHEMA),
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
    metadata: MetaData

    @declared_attr.directive
    def __tablename__(self) -> str:
        """Generate __tablename__ automatically using class name. Remove `ORM` prefix from it."""
        orm_class_name_prefix = "orm"
        cls_name = self.__name__.lower()
        if cls_name[: len(orm_class_name_prefix)] == orm_class_name_prefix:
            return cls_name[len(orm_class_name_prefix) :]
        else:
            return cls_name

    @declared_attr.directive
    def __table_args__(self) -> dict:
        """Generate __table_args__ with infomation about database schema"""
        return {"schema": settings_db.DB_SCHEMA}
