from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Annotated, Any, Self, cast

from attr import define
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from structlog.contextvars import bind_contextvars, unbind_contextvars

from app.domain.user import DomainUser
from app.infrastructure.repositories.user import RepositoryUserSql
from app.infrastructure.units_of_work.base_sql import UnitOfWorkSqlAlchemy
from app.system.config import Settings
from app.system.exceptions import InvalidJwtError, JwtExpiredError

# Use FastAPI default tools (dependencies) for OAuth2 authorization protocol
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/{Settings().general.BACKEND_API_PREFIX}/user/sign-in"
)
TokenDep = Annotated[str, Depends(oauth2_scheme)]

# Internal dependencies
uow_user = UnitOfWorkSqlAlchemy(RepositoryUserSql)
UowUserDep = Annotated[UnitOfWorkSqlAlchemy, Depends(uow_user)]


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
        self.user: DomainUser | None = None

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

    async def get_current_user(self) -> DomainUser:
        """Get user with email extracted from token and verify it"""
        async with self.uow:
            self.uow.repository = cast(RepositoryUserSql, self.uow.repository)
            self.user = await self.uow.repository.get_by_email(self.token_decoded.sub)
        self.user.verify_user()
        return self.user


async def verify_authorization(
    token_encoded: TokenDep, uow: UowUserDep
) -> AsyncGenerator[ServiceAuthorization, Any]:
    """Automatically enter into `ServiceAuthorization` context manager when used FastApi Depends"""
    async with ServiceAuthorization(token_encoded, uow) as service_auth:
        yield service_auth
