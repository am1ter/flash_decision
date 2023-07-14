from __future__ import annotations

from typing import TYPE_CHECKING

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from attrs import define, field
from pydantic import EmailStr, IPvAnyAddress, ValidationError, parse_obj_as

from app.domain.base import Agregate, Entity, ValueObject, field_relationship
from app.system.constants import AuthStatus, UserStatus
from app.system.exceptions import (
    EmailValidationError,
    IpAddressValidationError,
    UserDisabledError,
    WrongPasswordError,
)

if TYPE_CHECKING:
    from app.domain.session import DomainSession

password_hasher = PasswordHasher()


@define(kw_only=False, slots=False, frozen=True)
class Email(ValueObject):
    """Value Object to ensure invariants"""

    value: str = field()

    @value.validator
    def _validate_email(self, attribute: str, value: str) -> None:
        try:
            parse_obj_as(EmailStr, value)
        except ValidationError as e:
            raise EmailValidationError from e


@define(kw_only=False, slots=False, frozen=True)
class Password(ValueObject):
    """Value Object to ensure that password is always hashed"""

    value: str

    def hash_password(self) -> str:
        return password_hasher.hash(self.value)

    def verify_password(self, password_to_verify: str) -> bool:
        return password_hasher.verify(self.value, password_to_verify)


@define(kw_only=True, slots=False, hash=True)
class DomainUser(Agregate):
    """
    This class is the DDD Agregate.
    Represents a user with its credits and authentication functionality.
    """

    name: str
    email: Email = field(converter=Email)
    password: Password = field(converter=Password, repr=lambda _: "***")
    status: UserStatus
    auths: list[DomainAuth] = field_relationship(init=False)
    sessions: list[DomainSession] = field_relationship(init=False)

    def verify_user(self) -> None:
        # Check if user is not disabled
        if self.status == UserStatus.disabled:
            raise UserDisabledError

    @classmethod
    def sign_up(cls, name: str, email: str, password: str) -> DomainUser:
        hashed_password = Password(password).hash_password()
        new_user = cls(name=name, email=email, password=hashed_password, status=UserStatus.active)
        return new_user

    def sign_in(self, password_to_verify: str) -> None:
        self.verify_user()
        # Check password
        try:
            self.password.verify_password(password_to_verify)
        except VerifyMismatchError as e:
            raise WrongPasswordError from e

    def create_auth_sign_up(self, ip_address: str, http_user_agent: str) -> DomainAuth:
        new_auth = DomainAuth(
            user=self,
            ip_address=ip_address,
            http_user_agent=http_user_agent,
            status=AuthStatus.sign_up,
        )
        return new_auth

    def create_auth_sign_in(self, ip_address: str, http_user_agent: str) -> DomainAuth:
        new_auth = DomainAuth(
            user=self,
            ip_address=ip_address,
            http_user_agent=http_user_agent,
            status=AuthStatus.sign_in,
        )
        return new_auth

    def create_auth_wrong_pass(self, ip_address: str, http_user_agent: str) -> DomainAuth:
        new_auth = DomainAuth(
            user=self,
            ip_address=ip_address,
            http_user_agent=http_user_agent,
            status=AuthStatus.wrong_password,
        )
        return new_auth


@define(kw_only=False, slots=False, frozen=True)
class IpAddress(ValueObject):
    """Value Object to ensure invariants"""

    value: str = field()

    @value.validator
    def _validate_ip(self, attribute: str, value: str) -> None:
        try:
            parse_obj_as(IPvAnyAddress, value)
        except ValidationError as e:
            raise IpAddressValidationError from e


@define(kw_only=True, slots=False, hash=True)
class DomainAuth(Entity):
    """
    This class is the part of the DDD Agregate `User`.
    Represents information about each user's sign-in.
    """

    ip_address: IpAddress = field(converter=IpAddress)
    http_user_agent: str
    status: AuthStatus
    user: DomainUser = field_relationship(init=True)
