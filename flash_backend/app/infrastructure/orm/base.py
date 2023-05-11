from datetime import datetime
from typing import Annotated

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
