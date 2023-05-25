from __future__ import annotations

from attrs import define, field
from passlib.context import CryptContext

from app.domain.base import Entity, field_relationship
from app.system.constants import AuthStatus, UserStatus
from app.system.exceptions import UserDisabledError, WrongPasswordError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@define(kw_only=True, slots=False)
class DomainUser(Entity):
    """
    This class is the DDD Agregate.
    Represents a user with its credits and authentication functionality.
    """

    name: str
    email: str
    password: str = field(repr=False)
    status: UserStatus
    auths: list[DomainAuth] = field_relationship(init=False)

    @classmethod
    def create(
        cls, name: str, email: str, password: str, ip_address: str, http_user_agent: str
    ) -> DomainUser:
        password_hashed = pwd_context.hash(password)
        new_user = cls(name=name, email=email, password=password_hashed, status=UserStatus.active)

        DomainAuth.create_sign_up(
            user=new_user,
            http_user_agent=http_user_agent,
            ip_address=ip_address,
        )

        return new_user

    def _verify_password(self, password_to_verify: str) -> bool:
        return pwd_context.verify(password_to_verify, self.password)

    def _verify_user_is_enabled(self) -> bool:
        return self.status != UserStatus.disabled

    def sign_in(self, password: str, ip_address: str, http_user_agent: str) -> DomainAuth:
        # Check if user is not disabled
        if not self._verify_user_is_enabled():
            raise UserDisabledError

        # Check password
        if not self._verify_password(password):
            raise WrongPasswordError

        # Create auth
        auth = DomainAuth.create_sign_in(
            user=self,
            http_user_agent=http_user_agent,
            ip_address=ip_address,
        )

        return auth


@define(kw_only=True, slots=False)
class DomainAuth(Entity):
    """
    This class is the part of the DDD Agregate `User`.
    Represents information about each user's sign-in.
    """

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
