from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from passlib.context import CryptContext

from app.domain.base import Entity, field_relationship
from app.system.constants import UserStatus

if TYPE_CHECKING:
    from app.domain.auth import DomainAuth


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@define(kw_only=True, slots=False)
class DomainUser(Entity):
    name: str
    email: str
    password: str = field(repr=False)
    status: UserStatus
    auths: list[DomainAuth] = field_relationship(init=False)

    @classmethod
    def create(cls, name: str, email: str, password: str) -> DomainUser:
        password_hashed = pwd_context.hash(password)
        new_user = cls(name=name, email=email, password=password_hashed, status=UserStatus.active)
        return new_user

    def verify_password(self, password_to_verify: str) -> bool:
        return pwd_context.verify(password_to_verify, self.password)

    def verify_user_is_disabled(self) -> bool:
        return self.status == UserStatus.disabled
