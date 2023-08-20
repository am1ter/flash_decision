from datetime import datetime
from typing import Self

from attrs import define, field
from jose import ExpiredSignatureError, JWTError, jwt
from structlog.contextvars import bind_contextvars, unbind_contextvars

from app.domain.interfaces.repository import RepositoryUser
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.domain.user import User
from app.services.interfaces.service import Service
from app.system.config import Settings
from app.system.exceptions import InvalidJwtError, JwtExpiredError


@define
class JwtTokenDecoded:
    """Convert dict with token parameters to the object"""

    sub: str
    iat: datetime
    exp: datetime


@define(kw_only=False, slots=False, hash=True)
class ServiceAuthorization(Service):
    """Service for an endpoint that may only be accessed by authorized users only"""

    uow: UnitOfWork[RepositoryUser]
    token_encoded: str = field()
    token_decoded = field()
    user: User | None = field(default=None)

    @token_decoded.default
    def token_decoded_default(self) -> JwtTokenDecoded:
        return self._decode_token(self.token_encoded)

    async def __aenter__(self) -> Self:
        self.user = await self.get_current_user()
        bind_contextvars(user=self.user)
        return self

    async def __aexit__(self, *args) -> None:
        unbind_contextvars("user")

    def _decode_token(self, token_encoded: str) -> JwtTokenDecoded:
        """Decode JWT token, validate it, extract user's creds"""
        try:
            token_dec = jwt.decode(
                token_encoded, Settings().general.JWT_SECRET_KEY, Settings().general.JWT_ALGORITHM
            )
        except ExpiredSignatureError as e:
            raise JwtExpiredError from e
        except JWTError as e:
            raise InvalidJwtError from e
        return JwtTokenDecoded(**token_dec)

    async def get_current_user(self) -> User:
        """Get user with email extracted from token and verify it"""
        async with self.uow:
            self.user = await self.uow.repository.get_by_email(self.token_decoded.sub)
        self.user.verify_user()
        return self.user
