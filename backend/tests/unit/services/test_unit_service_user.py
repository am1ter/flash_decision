from copy import copy
from datetime import datetime
from typing import Self

import pytest
import pytest_asyncio
from jose import jwt
from uuid6 import uuid6

from app.api.schemas.user import ReqSignIn, ReqSignUp, ReqSystemInfo
from app.domain.user import DomainAuth, DomainUser
from app.infrastructure.repositories.base import Repository
from app.infrastructure.units_of_work.base import UnitOfWork
from app.services.user import JwtTokenEncoded, ServiceUser
from app.services.user_authorization import ServiceAuthorization, verify_authorization
from app.system.config import Settings
from app.system.constants import AuthStatus, UserStatus
from app.system.exceptions import (
    EmailValidationError,
    InvalidJwtError,
    IpAddressValidationError,
    JwtExpiredError,
    UserDisabledError,
    WrongPasswordError,
)

pytestmark = pytest.mark.asyncio


class RepositoryUserFake(Repository):
    def __init__(self) -> None:
        self.storage_user: dict[str, DomainUser] = {}
        self.storage_auth: dict[str, list[DomainAuth]] = {}

    def add(self, obj: DomainUser) -> None:  # type: ignore[override]
        if not hasattr(obj, "_id"):
            obj._id = uuid6()
        obj.datetime_create = datetime.utcnow()
        self.storage_user[obj._id] = obj
        self.storage_auth[obj._id] = list(obj.auths)

    async def get_by_id(self, _id: str) -> DomainUser:
        return self.storage_user[_id]

    async def get_by_email(self, email: str) -> DomainUser | None:
        user = [v for v in self.storage_user.values() if v.email.value == email]
        return user[0]


class UnitOfWorkUserFake(UnitOfWork):
    def __init__(self) -> None:
        self.repository = RepositoryUserFake()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        pass

    async def commit(self) -> None:
        pass


@pytest.fixture()
def uow_user() -> UnitOfWorkUserFake:
    return UnitOfWorkUserFake()


@pytest.fixture()
def service_user(uow_user: UnitOfWorkUserFake) -> ServiceUser:
    return ServiceUser(uow_user)  # type: ignore[arg-type]


@pytest.fixture()
def req_system_info() -> ReqSystemInfo:
    return ReqSystemInfo(ip_address="127.0.0.1", user_agent="Test")


@pytest_asyncio.fixture()
async def user_sign_up(
    service_user: ServiceUser, req_sign_up: ReqSignUp, req_system_info: ReqSystemInfo
) -> DomainUser:
    user = await service_user.sign_up(
        email=req_sign_up.email,
        name=req_sign_up.name,
        password=req_sign_up.password,
        ip_address=req_system_info.ip_address,
        user_agent=req_system_info.user_agent,
    )
    return user


@pytest_asyncio.fixture()
async def token_encoded(service_user: ServiceUser, user_sign_up: DomainUser) -> JwtTokenEncoded:
    token = await service_user.create_access_token(user_sign_up)
    return token


@pytest_asyncio.fixture()
async def service_auth(
    token_encoded: JwtTokenEncoded, uow_user: UnitOfWorkUserFake
) -> ServiceAuthorization:
    return ServiceAuthorization(token_encoded.access_token, uow_user)  # type: ignore[arg-type]


class TestServiceUser:
    async def test_sign_up_success(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_system_info: ReqSystemInfo,
    ) -> None:
        user = await service_user.sign_up(
            email=req_sign_up.email,
            name=req_sign_up.name,
            password=req_sign_up.password,
            ip_address=req_system_info.ip_address,
            user_agent=req_system_info.user_agent,
        )

        # Check user
        assert user is not None, "New user is not created"
        assert req_sign_up.email == user.email.value
        assert req_sign_up.name == user.name

        # Check password
        assert req_sign_up.password != user.password.value, "Password is not hashed"
        assert user.password.verify_password(req_sign_up.password), "Password hashed incorrectly"

        # Check auth
        assert len(service_user.uow.repository.storage_auth) == 1, "Auth not created"  # type: ignore[attr-defined]

    async def test_sign_up_failure_wrong_email(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_system_info: ReqSystemInfo,
    ) -> None:
        with pytest.raises(EmailValidationError):
            await service_user.sign_up(
                email="wrong@wrong",
                name=req_sign_up.name,
                password=req_sign_up.password,
                ip_address=req_system_info.ip_address,
                user_agent=req_system_info.user_agent,
            )

    async def test_sign_in_success(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_sign_in: ReqSignIn,
        req_system_info: ReqSystemInfo,
    ) -> None:
        user_sign_up = await service_user.sign_up(
            email=req_sign_up.email,
            name=req_sign_up.name,
            password=req_sign_up.password,
            ip_address=req_system_info.ip_address,
            user_agent=req_system_info.user_agent,
        )
        user_sign_in = await service_user.sign_in(
            username=req_sign_in.username,
            password=req_sign_in.password,
            ip_address=req_system_info.ip_address,
            user_agent=req_system_info.user_agent,
        )

        # Check user signed in
        assert user_sign_up == user_sign_in

        # Check auth record created
        sign_in_auths = service_user.uow.repository.storage_auth[user_sign_up._id]  # type: ignore[attr-defined]
        assert len(sign_in_auths) == 2, "Auths not created"
        assert sign_in_auths[0].user == user_sign_in, "Auths for sign in not created"

    async def test_sign_in_failure_user_disabled(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_sign_in: ReqSignIn,
        req_system_info: ReqSystemInfo,
    ) -> None:
        user_sign_up = await service_user.sign_up(
            email=req_sign_up.email,
            name=req_sign_up.name,
            password=req_sign_up.password,
            ip_address=req_system_info.ip_address,
            user_agent=req_system_info.user_agent,
        )
        assert user_sign_up is not None, "User is not created"
        user_sign_up.status = UserStatus.disabled
        with pytest.raises(UserDisabledError):
            await service_user.sign_in(
                username=req_sign_in.username,
                password=req_sign_in.password,
                ip_address=req_system_info.ip_address,
                user_agent=req_system_info.user_agent,
            )
        user_sign_up.status = UserStatus.active

    async def test_sign_in_failure_wrong_password(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_sign_in: ReqSignIn,
        req_system_info: ReqSystemInfo,
    ) -> None:
        user_sign_up = await service_user.sign_up(
            email=req_sign_up.email,
            name=req_sign_up.name,
            password=req_sign_up.password,
            ip_address=req_system_info.ip_address,
            user_agent=req_system_info.user_agent,
        )
        assert user_sign_up is not None, "User is not created"
        with pytest.raises(WrongPasswordError):
            await service_user.sign_in(
                username=req_sign_in.username,
                password="wrongPass",  # noqa: S106
                ip_address=req_system_info.ip_address,
                user_agent=req_system_info.user_agent,
            )
        auth_wrong_pass = service_user.uow.repository.storage_auth[user_sign_up._id][-1]  # type: ignore[attr-defined]
        assert auth_wrong_pass.status == AuthStatus.wrong_password

    async def test_auth_failure_wrong_ip(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_system_info: ReqSystemInfo,
    ) -> None:
        with pytest.raises(IpAddressValidationError):
            await service_user.sign_up(
                email=req_sign_up.email,
                name=req_sign_up.name,
                password=req_sign_up.password,
                ip_address="192.168.0.",
                user_agent=req_system_info.user_agent,
            )

    async def test_create_access_token(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_system_info: ReqSystemInfo,
    ) -> None:
        user = await service_user.sign_up(
            email=req_sign_up.email,
            name=req_sign_up.name,
            password=req_sign_up.password,
            ip_address=req_system_info.ip_address,
            user_agent=req_system_info.user_agent,
        )
        token_encoded = await service_user.create_access_token(user)
        token_decoded = jwt.decode(
            token=token_encoded.access_token, key=Settings().general.JWT_SECRET_KEY
        )
        assert token_decoded["sub"] == user.email.value
        assert token_decoded["exp"] >= token_decoded["iat"]


class TestServiceAuthorization:
    async def test_authorization_success(
        self, service_auth: ServiceAuthorization, user_sign_up: DomainUser
    ) -> None:
        user_by_token = await service_auth.get_current_user()
        assert user_by_token == user_sign_up

    async def test_authorization_failure_invalid(
        self, token_encoded: JwtTokenEncoded, uow_user: UnitOfWorkUserFake
    ) -> None:
        token_encoded_invalid = token_encoded.access_token + "wrong"
        with pytest.raises(InvalidJwtError):
            ServiceAuthorization(token_encoded_invalid, uow_user)  # type: ignore[arg-type]

    async def test_authorization_failure_expired(
        self, token_encoded: JwtTokenEncoded, uow_user: UnitOfWorkUserFake
    ) -> None:
        token_encoded_valid = token_encoded.access_token
        token_decoded_valid = jwt.decode(
            token=token_encoded_valid, key=Settings().general.JWT_SECRET_KEY
        )
        token_decoded_invalid = copy(token_decoded_valid)
        token_decoded_invalid["exp"] = token_decoded_invalid["iat"] - 100
        token_encoded_invalid = jwt.encode(
            token_decoded_invalid,
            Settings().general.JWT_SECRET_KEY,
            Settings().general.JWT_ALGORITHM,
        )
        with pytest.raises(JwtExpiredError):
            ServiceAuthorization(token_encoded_invalid, uow_user)  # type: ignore[arg-type]

    async def test_verify_authorization(
        self, token_encoded: JwtTokenEncoded, uow_user: UnitOfWorkUserFake
    ) -> None:
        service_auth_gen = verify_authorization(token_encoded.access_token, uow_user)  # type: ignore[arg-type]
        service_auth = await anext(service_auth_gen)
        assert isinstance(service_auth, ServiceAuthorization)
        assert isinstance(service_auth.user, DomainUser)
