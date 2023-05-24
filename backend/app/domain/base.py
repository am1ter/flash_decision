from datetime import datetime
from typing import Any

from attrs import define, field


def field_relationship(*, init: bool) -> Any:
    """Mark domain attribute as ORM relationships (mapped with ORM in map_imperatively() func)"""
    return field(init=init, repr=False, eq=False)


@define(kw_only=True, slots=False)
class Entity:
    """Meta class for all domain entities"""

    id: int = field(init=False)
    datetime_create: datetime = field(init=False, repr=False)
