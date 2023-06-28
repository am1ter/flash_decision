import uuid

import pytest

from app.api.schemas.user import ReqSignIn, ReqSignUp
from app.domain.user import DomainUser
from app.system.constants import UserStatus


@pytest.fixture()
def user_domain() -> DomainUser:
    return DomainUser(
        email=f"test-user-{uuid.uuid4()}@alekseisemenov.ru",
        name="test-user",
        password=str(uuid.uuid4()),
        status=UserStatus.active,
    )


@pytest.fixture(scope="module")
def req_sign_up() -> ReqSignUp:
    return ReqSignUp(
        email=f"test-user-{uuid.uuid4()}@alekseisemenov.ru",
        name="test-user",
        password=str(uuid.uuid4()),
    )


@pytest.fixture(scope="module")
def req_sign_in(req_sign_up: ReqSignUp) -> ReqSignIn:
    return ReqSignIn(username=req_sign_up.email, password=req_sign_up.password)
