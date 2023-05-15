from datetime import datetime

from attrs import define, field


@define(kw_only=True, slots=False)
class Entity:
    """Meta class for all domain entities"""

    id: int = field(init=False)
    datetime_create: datetime = field(init=False)
