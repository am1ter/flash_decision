from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from app.domain.base import Entity
from app.system.constants import UserStatus

if TYPE_CHECKING:
    from app.domain.auth import DomainAuth


@define(kw_only=True, slots=False)
class DomainUser(Entity):
    name: str
    email: str
    password: str
    status: UserStatus

    # ORM relationships for map_imperatively()
    auths: list[DomainAuth] = field(init=False)
