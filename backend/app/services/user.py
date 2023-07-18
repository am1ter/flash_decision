from datetime import datetime, timedelta
from typing import Annotated, cast

import structlog
from attrs import define
from fastapi import Depends
from jose import jwt

from app.api.schemas.user import ReqSignIn, ReqSignUp, ReqSystemInfo
from app.domain.user import DomainUser
from app.infrastructure.repositories.user import RepositoryUserSQL
from app.infrastructure.units_of_work.base_sql import UnitOfWorkSQLAlchemy
from app.system.config import Settings
from app.system.exceptions import DbObjectNotFoundError, UserNotFoundError, WrongPasswordError

# Create logger
logger = structlog.get_logger()

# Internal dependencies
uow_user = UnitOfWorkSQLAlchemy(RepositoryUserSQL)
UowUserDep = Annotated[UnitOfWorkSQLAlchemy, Depends(uow_user)]


@define
class JwtTokenEncoded:
    """Use the object instead of the raw dict for encoded JWT"""

    access_token: str
    token_type: str = "bearer"


class ServiceUser:
    """User manager class"""

    def __init__(self, uow: UowUserDep) -> None:
        self.uow = uow

    async def get_user_by_email(self, email: str) -> DomainUser:
        try:
            self.uow.repository = cast(RepositoryUserSQL, self.uow.repository)
            return await self.uow.repository.get_by_email(email)
        except DbObjectNotFoundError as e:
            raise UserNotFoundError from e

    async def sign_up(self, req: ReqSignUp, req_system_info: ReqSystemInfo) -> DomainUser:
        # Create user
        user = DomainUser.sign_up(**req.dict())
        user.create_auth_sign_up(
            ip_address=req_system_info.ip_address, http_user_agent=req_system_info.user_agent
        )
        # Save user to the database
        async with self.uow:
            self.uow.repository.add(user)
            await self.uow.commit()
        await logger.ainfo_finish(cls=self.__class__, show_func_name=True, user=user)
        return user

    async def sign_in(self, req: ReqSignIn, req_system_info: ReqSystemInfo) -> DomainUser:
        async with self.uow:
            # Get user with specified email, check password and status
            user = await self.get_user_by_email(req.username)
            try:
                user.sign_in(req.password)
            except WrongPasswordError as e:
                # Record sign-in attempt to the database
                auth = user.create_auth_wrong_pass(
                    req_system_info.ip_address, req_system_info.user_agent
                )
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
            auth = user.create_auth_sign_in(req_system_info.ip_address, req_system_info.user_agent)
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
