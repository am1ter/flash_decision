from datetime import datetime, timedelta

import structlog
from attrs import define
from jose import jwt

from app.domain.repository import RepositoryUser
from app.domain.unit_of_work import UnitOfWork
from app.domain.user import DomainUser
from app.services.base import Service
from app.system.config import Settings
from app.system.exceptions import DbObjectNotFoundError, UserNotFoundError, WrongPasswordError

# Create logger
logger = structlog.get_logger()


@define
class JwtTokenEncoded:
    """Use the object instead of the raw dict for encoded JWT"""

    access_token: str
    token_type: str = "bearer"


@define(kw_only=False, slots=False, hash=True)
class ServiceUser(Service):
    """User manager class"""

    uow: UnitOfWork[RepositoryUser]

    async def get_user_by_email(self, email: str) -> DomainUser:
        try:
            return await self.uow.repository.get_by_email(email)
        except DbObjectNotFoundError as e:
            raise UserNotFoundError from e

    async def sign_up(
        self, email: str, name: str, password: str, ip_address: str, user_agent: str
    ) -> DomainUser:
        # Create user
        user = DomainUser.sign_up(name=name, email=email, password=password)
        user.create_auth_sign_up(ip_address=ip_address, http_user_agent=user_agent)
        # Save user to the database
        async with self.uow:
            self.uow.repository.add(user)
            await self.uow.commit()
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, user=user)
        return user

    async def sign_in(
        self, username: str, password: str, ip_address: str, user_agent: str
    ) -> DomainUser:
        async with self.uow:
            # Get user with specified email, check password and status
            user = await self.get_user_by_email(username)
            try:
                user.sign_in(password)
            except WrongPasswordError as e:
                # Record sign-in attempt to the database
                auth = user.create_auth_wrong_pass(ip_address, user_agent)
                self.uow.repository.add(user)
                await self.uow.commit()
                await logger.ainfo(
                    "Sign-in attempt with wrong password",
                    cls=self.__class__,
                    show_func_name=True,
                    user=user,
                )
                raise WrongPasswordError from e
            # Record success
            auth = user.create_auth_sign_in(ip_address, user_agent)
            self.uow.repository.add(user)
            await self.uow.commit()
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, user=user, auth=auth)
        return user

    async def create_access_token(self, user: DomainUser) -> JwtTokenEncoded:
        """Create JWT according its specification"""
        payload = {
            "sub": user.email.value,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow()
            + timedelta(minutes=Settings().general.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        encoded_jwt_str = jwt.encode(
            payload, Settings().general.JWT_SECRET_KEY, Settings().general.JWT_ALGORITHM
        )
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, user=user)
        return JwtTokenEncoded(access_token=encoded_jwt_str)
