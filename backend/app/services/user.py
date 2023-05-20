from typing import Annotated

from fastapi import Depends

from app.api.schemas.user import ReqSignIn, ReqSignUp, ReqSystemInfo
from app.domain.auth import DomainAuth
from app.domain.user import DomainUser
from app.infrastructure.repositories.user import repository_user
from app.system.exceptions import UserDisabledError, UserNotFoundError, WrongPasswordError
from app.system.logger import logger


class ServiceUser:
    """User manager class"""

    def __init__(self, repository: repository_user) -> None:
        self.repository = repository

    async def sign_up(self, req: ReqSignUp, req_system_info: ReqSystemInfo) -> DomainUser:
        # Create user
        user = DomainUser.create(**req.dict())
        self.repository.add(user)

        # Create auth
        auth = DomainAuth.create_sign_up(
            user=user,
            http_user_agent=req_system_info.user_agent,
            ip_address=req_system_info.ip_address,
        )
        self.repository.add(auth)

        # Finalize
        await self.repository.save()
        logger.info_finish(cls=self.__class__, show_func_name=True, user=user)
        return user

    async def sign_in(self, req: ReqSignIn, req_system_info: ReqSystemInfo) -> DomainUser:
        # Get user with specified email
        user = await self.repository.get_by_email(req.email)

        # Check if email is valid
        if not user:
            raise UserNotFoundError

        # Check if user is not disabled
        if user.verify_user_is_disabled():
            raise UserDisabledError

        # Check password
        if not user.verify_password(req.password):
            raise WrongPasswordError

        # Create auth
        auth = DomainAuth.create_sign_up(
            user=user,
            http_user_agent=req_system_info.user_agent,
            ip_address=req_system_info.ip_address,
        )
        self.repository.add(auth)
        await self.repository.save()

        # Finalize
        logger.info_finish(cls=self.__class__, show_func_name=True, user=user)
        return user


# For dependancy injection
ServiceUserDep = Annotated[ServiceUser, Depends()]
