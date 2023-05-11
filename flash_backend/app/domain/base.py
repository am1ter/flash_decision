from datetime import datetime

from attrs import define


@define(kw_only=True, hash=True, slots=False)
class Entity:
    """Meta class for all domain entities"""

    id: int | None = None
    datetime_create: datetime | None = None
