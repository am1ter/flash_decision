from datetime import datetime
from enum import Enum
from typing import Any, Self

from attrs import Attribute, asdict, define, field
from uuid6 import UUID, uuid6


def field_relationship(*, init: bool) -> Any:
    """Mark domain attribute as ORM relationships (mapped with ORM in map_imperatively() func)"""
    return field(init=init, repr=False, eq=False)


@define(kw_only=False, slots=False, frozen=True)
class ValueObject:
    """
    A small simple object with only one attribute.
    Used for supporting entities invariants.
    https://martinfowler.com/bliki/ValueObject.html
    """

    value: Any

    def __composite_values__(self) -> tuple[Any]:
        """
        Add support of using attrs lib instances to map_imperatively() function.
        Composite Columns (in SQLAlchemy 2.0) do not support the `attrs` lib instances.
        https://docs.sqlalchemy.org/en/20/orm/composites.html#using-legacy-non-dataclasses
        P.S. It is not the database dependency
        """
        return (self.value,)


@define(kw_only=False, slots=False, frozen=True)
class ValueObjectJson:
    """
    A small simple object with some attributes.
    Used for converting attrs objects from/to jsons.
    https://martinfowler.com/bliki/ValueObject.html
    """

    def __composite_values__(self) -> tuple[dict[str, str]]:
        return (asdict(self, value_serializer=custom_serializer),)

    @classmethod
    def from_json(cls, value: dict[str, str]) -> Self:
        return cls(**value)


@define(kw_only=True, slots=False)
class Entity:
    """
    Meta class for all domain entities.
    https://martinfowler.com/bliki/EvansClassification.html
    """

    _id: UUID = field(factory=uuid6, repr=False)
    datetime_create: datetime = field(factory=datetime.utcnow, repr=False)


class Agregate(Entity):
    """
    Used for entity object (root) that controls other entities (components).
    https://martinfowler.com/bliki/DDD_Aggregate.html
    """


def custom_serializer(instance: type, field: Attribute, value: Any) -> Any:
    """
    It is custom serializer for `attrs` asdict() method.
    Used to avoid convertation Value Objects to dicts, etc.
    """
    match value:
        case ValueObject():
            return value.value
        case Enum():
            return value.value
        case _:
            return value
