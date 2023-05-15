from typing import Annotated

from fastapi import Depends

from app.api.schemas.user import ReqSignUp, ReqSystemInfo
from app.domain.auth import AuthStatus, DomainAuth
from app.domain.user import DomainUser, UserStatus
from app.infrastructure.repositories.user import repository_user


class ServiceUser:
    """User manager class"""

    def __init__(self, repository: repository_user) -> None:
        self.repository = repository

    async def create_user(self, req: ReqSignUp, req_system_info: ReqSystemInfo) -> DomainUser:
        # Create user
        new_user = DomainUser(**req.dict(), status=UserStatus.active)
        self.repository.add(new_user)
        await self.repository.flush()
        await self.repository.refresh(new_user)

        # Create auth
        first_auth = DomainAuth(
            user_id=new_user.id,
            http_user_agent=req_system_info.user_agent,
            ip_address=req_system_info.ip_address,
            status=AuthStatus.sign_up,
        )
        self.repository.add(first_auth)
        await self.repository.save()

        # Return
        return new_user


# For dependancy injection
ServiceUserDep = Annotated[ServiceUser, Depends()]
