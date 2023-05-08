from datetime import datetime

from attrs import define


@define(kw_only=True, hash=True)
class Entity:
    """Meta class for all domain entities"""

    id: int | None = None
    datetime_create: datetime | None = None
