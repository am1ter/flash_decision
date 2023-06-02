from datetime import datetime
from typing import Any

from attrs import define, field


def field_relationship(*, init: bool) -> Any:
    """Mark domain attribute as ORM relationships (mapped with ORM in map_imperatively() func)"""
    return field(init=init, repr=False, eq=False)


@define(kw_only=False, slots=False, frozen=True)
class ValueObject:
    value: Any

    def __composite_values__(self) -> tuple[Any]:
        """
        Add support of using attrs lib instances to map_imperatively() function.
        Composite Columns (in SQLAlchemy 2.0) do not support the `attrs` lib instances.
        https://docs.sqlalchemy.org/en/20/orm/composites.html#using-legacy-non-dataclasses
        P.S. It is not the database dependency
        """
        return (self.value,)


@define(kw_only=True, slots=False)
class Entity:
    """Meta class for all domain entities"""

    id: int = field(init=False)
    datetime_create: datetime = field(init=False, repr=False)
