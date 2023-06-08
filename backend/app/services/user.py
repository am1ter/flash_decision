from datetime import datetime, timedelta
from typing import Annotated, cast

from attrs import define
from fastapi import Depends
from jose import jwt

from app.api.schemas.user import ReqSignIn, ReqSignUp, ReqSystemInfo
from app.domain.user import DomainUser
from app.infrastructure.repositories.user import RepositoryUserSQL
from app.infrastructure.units_of_work.base import UnitOfWorkSQLAlchemy
from app.system.config import settings
from app.system.exceptions import DbObjectNotFoundError, UserNotFoundError
from app.system.logger import logger

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
        user = DomainUser.create(
            **req.dict(),
            ip_address=req_system_info.ip_address,
            http_user_agent=req_system_info.user_agent
        )
        # Save user to the database
        async with self.uow:
            self.uow.repository.add(user)
            await self.uow.commit()
        logger.info_finish(cls=self.__class__, show_func_name=True, user=user)
        return user

    async def sign_in(self, req: ReqSignIn, req_system_info: ReqSystemInfo) -> DomainUser:
        async with self.uow:
            # Get user with specified email, check password and status
            user = await self.get_user_by_email(req.username)
            user.verify_user(req.password)

            # Create auth and update the database
            auth = user.create_auth(req_system_info.ip_address, req_system_info.user_agent)
            self.uow.repository.add(user)

            # Finalize
            await self.uow.commit()
        logger.info_finish(cls=self.__class__, show_func_name=True, user=user, auth=auth)
        return user

    def create_access_token(self, user: DomainUser) -> JwtTokenEncoded:
        """Create JWT according its specification"""
        payload = {
            "sub": user.email.value,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        encoded_jwt_str = jwt.encode(payload, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        logger.info_finish(cls=self.__class__, show_func_name=True, user=user)
        return JwtTokenEncoded(access_token=encoded_jwt_str)
