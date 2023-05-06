from datetime import datetime
from typing import Annotated

from sqlalchemy import MetaData, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import mapped_column, registry

from app.system.config import settings_db

# Custom `python types` to `database columns` mappings
int_pk = Annotated[int, mapped_column(primary_key=True)]
str_unq = Annotated[str, mapped_column(unique=True, index=True)]
datetime_current = Annotated[datetime, mapped_column(server_default=func.now())]


reg = registry()


@reg.mapped_as_dataclass
@as_declarative()
class Base:
    __name__: str
    metadata: MetaData

    @declared_attr.directive
    def __tablename__(self) -> str:
        """Generate __tablename__ automatically"""
        return self.__name__.capitalize()

    @declared_attr.directive
    def __table_args__(self) -> dict:
        """Generate __table_args__ with infomation about database schema"""
        return {"schema": settings_db.DB_SCHEMA}
