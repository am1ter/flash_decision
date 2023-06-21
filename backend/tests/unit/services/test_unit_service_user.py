from copy import copy

import pytest
from jose import jwt

from app.api.schemas.user import ReqSignIn, ReqSignUp, ReqSystemInfo
from app.services.user import ServiceUser
from app.system.config import settings
from app.system.constants import AuthStatus, UserStatus
from app.system.exceptions import (
    EmailValidationError,
    IpAddressValidationError,
    UserDisabledError,
    WrongPasswordError,
)

pytestmark = pytest.mark.asyncio


class TestServiceUser:
    async def test_sign_up_success(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_system_info: ReqSystemInfo,
    ) -> None:
        user = await service_user.sign_up(req_sign_up, req_system_info)

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
        req_sign_up_wrong_email = copy(req_sign_up)
        req_sign_up_wrong_email.email = "wrong@wrong"
        with pytest.raises(EmailValidationError):
            await service_user.sign_up(req_sign_up_wrong_email, req_system_info)

    async def test_sign_in_success(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_sign_in: ReqSignIn,
        req_system_info: ReqSystemInfo,
    ) -> None:
        user_sign_up = await service_user.sign_up(req_sign_up, req_system_info)
        user_sign_in = await service_user.sign_in(req_sign_in, req_system_info)

        # Check user signed in
        assert user_sign_up == user_sign_in

        # Check auth record created
        sign_in_auths = service_user.uow.repository.storage_auth[user_sign_up.id]  # type: ignore[attr-defined]
        assert len(sign_in_auths) == 2, "Auths not created"
        assert sign_in_auths[0].user == user_sign_in, "Auths for sign in not created"

    async def test_sign_in_failure_user_disabled(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_sign_in: ReqSignIn,
        req_system_info: ReqSystemInfo,
    ) -> None:
        user_sign_up = await service_user.sign_up(req_sign_up, req_system_info)
        assert user_sign_up is not None, "User is not created"
        user_sign_up.status = UserStatus.disabled
        with pytest.raises(UserDisabledError):
            await service_user.sign_in(req_sign_in, req_system_info)
        user_sign_up.status = UserStatus.active

    async def test_sign_in_failure_wrong_password(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_sign_in: ReqSignIn,
        req_system_info: ReqSystemInfo,
    ) -> None:
        user_sign_up = await service_user.sign_up(req_sign_up, req_system_info)
        assert user_sign_up is not None, "User is not created"
        req_sign_in.password = "wrongPass"  # noqa: S105
        with pytest.raises(WrongPasswordError):
            await service_user.sign_in(req_sign_in, req_system_info)
        auth_wrong_pass = service_user.uow.repository.storage_auth[user_sign_up.id][-1]  # type: ignore[attr-defined]
        assert auth_wrong_pass.status == AuthStatus.wrong_password

    async def test_auth_failure_wrong_ip(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_system_info: ReqSystemInfo,
    ) -> None:
        req_system_info_wrong_ip = copy(req_system_info)
        req_system_info_wrong_ip.ip_address = "192.168.0."
        with pytest.raises(IpAddressValidationError):
            await service_user.sign_up(req_sign_up, req_system_info_wrong_ip)

    async def test_create_access_token(
        self,
        service_user: ServiceUser,
        req_sign_up: ReqSignUp,
        req_system_info: ReqSystemInfo,
    ) -> None:
        user = await service_user.sign_up(req_sign_up, req_system_info)
        token_encoded = await service_user.create_access_token(user)
        token_decoded = jwt.decode(token=token_encoded.access_token, key=settings.JWT_SECRET_KEY)
        assert token_decoded["sub"] == user.email.value
        assert token_decoded["exp"] >= token_decoded["iat"]
