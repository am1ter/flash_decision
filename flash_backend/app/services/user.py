from typing import Annotated

from fastapi import Depends

from app.api.schemas.base import ReqMeta
from app.api.schemas.user import ReqSignUp
from app.domain.user import User, UserStatus
from app.infrastructure.repositories.user import repository_user


class ServiceUser:
    """User manager class"""

    def __init__(self, repository: repository_user) -> None:
        self.repository = repository

    async def create_user(self, req: ReqSignUp) -> None:
        new_user = User(**req.dict(), status=UserStatus.active)
        self.repository.add(new_user)
        await self.repository.save()

    async def get_user_by_request(self, req: ReqMeta) -> User | None:
        user = await self.repository.get_by_email(req.email)
        return user


# For dependancy injection
ServiceUserDep = Annotated[ServiceUser, Depends()]
