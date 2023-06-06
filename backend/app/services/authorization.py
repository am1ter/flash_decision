from datetime import datetime
from typing import Annotated

from attr import define
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

from app.domain.user import DomainUser
from app.services.user import ServiceUserDep
from app.system.config import settings
from app.system.exceptions import InvalidJwtError, JwtExpiredError

# Use FastAPI default tools (dependencies) for OAuth2 authorization protocol
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/sign-in")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


@define
class JwtTokenDecoded:
    """Convert dict with token parameters to the object"""

    sub: str
    iat: datetime
    exp: datetime


class ServiceAuthorization:
    """Service for an endpoint that may only be accessed by authorized users only"""

    def __init__(self, token_encoded: TokenDep, service_user: ServiceUserDep) -> None:
        self.service_user = service_user
        self.token_decoded = self._decode_token(token_encoded)

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
        """Get user with specific email and verify it"""
        user = await self.service_user.get_user_by_email(self.token_decoded.sub)
        user.verify_user()
        return user


# For dependancy injection
ServiceAuthorizationDep = Annotated[ServiceAuthorization, Depends()]
