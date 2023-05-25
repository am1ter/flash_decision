from typing import Annotated

from fastapi import Depends

from app.api.schemas.user import ReqSignIn, ReqSignUp, ReqSystemInfo
from app.domain.user import DomainUser
from app.infrastructure.repositories.user import repository_user
from app.system.exceptions import DbObjectNotFoundError, UserNotFoundError
from app.system.logger import logger


class ServiceUser:
    """User manager class"""

    def __init__(self, repository: repository_user) -> None:
        self.repository = repository

    async def sign_up(self, req: ReqSignUp, req_system_info: ReqSystemInfo) -> DomainUser:
        # Create user
        user = DomainUser.create(
            **req.dict(),
            ip_address=req_system_info.ip_address,
            http_user_agent=req_system_info.user_agent
        )
        self.repository.add(user)

        # Finalize
        await self.repository.save()
        logger.info_finish(cls=self.__class__, show_func_name=True, user=user)
        return user

    async def sign_in(self, req: ReqSignIn, req_system_info: ReqSystemInfo) -> DomainUser:
        # Get user with specified email
        try:
            user = await self.repository.get_by_email(req.email)
        except DbObjectNotFoundError as e:
            raise UserNotFoundError from e

        # Check password, status, create auth for user
        auth = user.sign_in(req.password, req_system_info.ip_address, req_system_info.user_agent)

        # Update user with new auth
        self.repository.add(user)

        # Finalize
        await self.repository.save()
        logger.info_finish(cls=self.__class__, show_func_name=True, user=user, auth=auth)
        return user


# For dependancy injection
ServiceUserDep = Annotated[ServiceUser, Depends()]
