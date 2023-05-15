from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from app.domain.base import Entity
from app.system.constants import AuthStatus

if TYPE_CHECKING:
    from app.domain.user import DomainUser


@define(kw_only=True, hash=True, slots=False)
class DomainAuth(Entity):
    user_id: int
    ip_address: str
    http_user_agent: str
    status: AuthStatus

    # ORM relationships for map_imperatively()
    user: DomainUser = field(init=False)
