from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from random import randint
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from app.api.schemas.user import ReqSignIn, ReqSignUp, ReqSystemInfo
from app.domain.user import DomainAuth, DomainUser
from app.infrastructure.repositories.base import Repository
from app.infrastructure.units_of_work.base import UnitOfWork
from app.services.user import ServiceUser

pytestmark = pytest.mark.asyncio


@asynccontextmanager
async def fake_db_connection() -> AsyncGenerator[AsyncConnection, Any]:
    engine = create_async_engine("sqlite+aiosqlite://")
    conn = await engine.connect()
    try:
        yield conn
    finally:
        await conn.close()


class RepositoryUserFake(Repository):
    def __init__(self) -> None:
        self.storage_user: dict[int, DomainUser] = {}
        self.storage_auth: dict[int, list[DomainAuth]] = {}

    def add(self, obj: DomainUser) -> None:  # type: ignore[override]
        obj.id = randint(1, 1000)
        obj.datetime_create = datetime.utcnow()
        self.storage_user[obj.id] = obj
        self.storage_auth[obj.id] = list(obj.auths)

    async def save(self) -> None:
        pass

    async def flush(self) -> None:
        pass

    async def refresh(self, object: DomainUser) -> None:
        pass

    async def get_by_id(self, id: int) -> DomainUser:
        return self.storage_user[id]

    async def get_by_email(self, email: str) -> DomainUser | None:
        user = [v for v in self.storage_user.values() if v.email.value == email]
        return user[0]


class UnitOfWorkUserFake(UnitOfWork):
    def __init__(self) -> None:
        self.repository = RepositoryUserFake()

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


@pytest.fixture()
def uow_user() -> UnitOfWorkUserFake:
    return UnitOfWorkUserFake()


@pytest.fixture()
def service_user(uow_user: UnitOfWorkUserFake) -> ServiceUser:
    return ServiceUser(uow_user)  # type: ignore[arg-type]


@pytest.fixture()
def req_sign_up() -> DomainUser:
    return ReqSignUp(
        email="test-signup@alekseisemenov.ru",
        name="test-signup",
        password="uc8a&Q!W",  # noqa: S106
    )


@pytest.fixture()
def req_sign_in(req_sign_up: DomainUser) -> DomainUser:
    return ReqSignIn(username=req_sign_up.email, password=req_sign_up.password)


@pytest.fixture()
def req_system_info() -> ReqSystemInfo:
    return ReqSystemInfo(ip_address="127.0.0.1", user_agent="Test")


@pytest_asyncio.fixture()
async def user_sign_up(
    service_user: ServiceUser, req_sign_up: ReqSignUp, req_system_info: ReqSystemInfo
) -> DomainUser:
    user = await service_user.sign_up(req_sign_up, req_system_info)
    return user
