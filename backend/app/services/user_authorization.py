from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Annotated, Any, Self, cast

from attr import define
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from structlog.contextvars import bind_contextvars, unbind_contextvars

from app.domain.user import DomainUser
from app.infrastructure.repositories.user import RepositoryUserSQL
from app.infrastructure.units_of_work.base import UnitOfWorkSQLAlchemy
from app.system.config import settings
from app.system.exceptions import InvalidJwtError, JwtExpiredError

# Use FastAPI default tools (dependencies) for OAuth2 authorization protocol
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/{settings.BACKEND_API_PREFIX}/user/sign-in")
TokenDep = Annotated[str, Depends(oauth2_scheme)]

# Internal dependencies
uow_user = UnitOfWorkSQLAlchemy(RepositoryUserSQL)
UowUserDep = Annotated[UnitOfWorkSQLAlchemy, Depends(uow_user)]


@define
class JwtTokenDecoded:
    """Convert dict with token parameters to the object"""

    sub: str
    iat: datetime
    exp: datetime


class ServiceAuthorization:
    """Service for an endpoint that may only be accessed by authorized users only"""

    def __init__(self, token_encoded: TokenDep, uow: UowUserDep) -> None:
        self.uow = uow
        self.token_decoded = self._decode_token(token_encoded)

    async def __aenter__(self) -> Self:
        self.user = await self.get_current_user()
        bind_contextvars(user=self.user)
        return self

    async def __aexit__(self, *args) -> None:
        unbind_contextvars("user")

    def _decode_token(self, token_encoded: str) -> JwtTokenDecoded:
        """Decode JWT token, validate it, extract user's creds"""
        try:
            token_dec = jwt.decode(token_encoded, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        except ExpiredSignatureError as e:
            raise JwtExpiredError from e
        except JWTError as e:
            raise InvalidJwtError from e
        return JwtTokenDecoded(**token_dec)

    async def get_current_user(self) -> DomainUser:
        """Get user with email extracted from token and verify it"""
        async with self.uow:
            self.uow.repository = cast(RepositoryUserSQL, self.uow.repository)
            user = await self.uow.repository.get_by_email(self.token_decoded.sub)
        user.verify_user()
        return user


async def verify_authorization(
    token_encoded: TokenDep, uow: UowUserDep
) -> AsyncGenerator[ServiceAuthorization, Any]:
    """Automatically enter into `ServiceAuthorization` context manager when used FastApi Depends"""
    async with ServiceAuthorization(token_encoded, uow) as service_auth:
        yield service_auth
