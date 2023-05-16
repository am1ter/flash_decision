from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define

from app.domain.base import Entity, field_relationship
from app.system.constants import AuthStatus

if TYPE_CHECKING:
    from app.domain.user import DomainUser


@define(kw_only=True, slots=False)
class DomainAuth(Entity):
    ip_address: str
    http_user_agent: str
    status: AuthStatus
    user: DomainUser = field_relationship(init=True)

    @classmethod
    def create_sign_up(cls, user: DomainUser, ip_address: str, http_user_agent: str) -> DomainAuth:
        new_auth = cls(
            user=user,
            ip_address=ip_address,
            http_user_agent=http_user_agent,
            status=AuthStatus.sign_up,
        )
        return new_auth

    @classmethod
    def create_sign_in(cls, user: DomainUser, ip_address: str, http_user_agent: str) -> DomainAuth:
        new_auth = cls(
            user=user,
            ip_address=ip_address,
            http_user_agent=http_user_agent,
            status=AuthStatus.sign_in,
        )
        return new_auth
