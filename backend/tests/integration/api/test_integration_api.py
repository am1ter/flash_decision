from __future__ import annotations

from contextlib import suppress

import pytest
import requests
from authlib.integrations.requests_client import OAuth2Auth, OAuth2Session

from app.api.schemas.session import ReqSession, RespSessionOptions
from app.api.schemas.support import RespDataHealthcheck
from app.api.schemas.user import ReqSignIn, ReqSignUp, RespSignIn, RespSignUp
from app.system.config import Settings
from app.system.constants import SessionBarsnumber, SessionMode
from app.system.exceptions import ProviderRateLimitExceededError


@pytest.fixture()
def oauth2(req_sign_in: ReqSignIn) -> OAuth2Auth:
    client = OAuth2Session()
    token_endpoint = f"{Settings().general.BACKEND_URL}/user/sign-in"
    token = client.fetch_token(
        token_endpoint, username=req_sign_in.username, password=req_sign_in.password
    )
    auth = OAuth2Auth(token)
    assert "errors" not in token, "Authentification token generation error"
    return auth


class Response:
    def __init__(self, response: requests.Response) -> None:
        self.response = response
        self.status = self.response.status_code
        self.url = self.response.url
        self._read_json()

    def __repr__(self) -> str:
        return f"<Response({self.status=}, {self.errors=}, {self.url=})>"

    def _read_json(self) -> None:
        try:
            self.json = self.response.json()
        except requests.JSONDecodeError:
            pass
        else:
            self.meta = self.json.get("meta")
            self.data = self.json.get("data")
            self.errors = self.json.get("errors")

    def assert_status_code(self, status_code: int) -> Response:
        assert self.response.status_code == status_code, f"Wrong status code for {self}"
        return self


class TestBackendDocs:
    def test_fastapi_docs_available(self) -> None:
        settings = Settings().general
        base_url = (
            f"{settings.BACKEND_PROTOCOL}://{settings.BACKEND_HOST}:{settings.BACKEND_PORT!s}"
        )
        r = requests.get(f"{base_url}/docs")
        response = Response(r)
        response.assert_status_code(200)


class TestBackendSupport:
    def test_run_healthcheck(self) -> None:
        r = requests.get(f"{Settings().general.BACKEND_URL}/support/healthcheck")
        response = Response(r)
        response.assert_status_code(200)
        data_model = RespDataHealthcheck(**response.data)
        assert data_model is not None
        assert data_model.is_app_up
        assert data_model.is_db_up


class TestBackendUser:
    @pytest.mark.dependency()
    def test_sign_up(self, req_sign_up: ReqSignUp) -> None:
        r = requests.post(f"{Settings().general.BACKEND_URL}/user/sign-up", json=req_sign_up.dict())
        response = Response(r)
        response.assert_status_code(200)
        data_model = RespSignUp(**response.response.json())
        assert data_model is not None
        assert data_model.email == req_sign_up.email

    @pytest.mark.dependency(depends=["TestBackendUser::test_sign_up"])
    def test_sign_in(self, req_sign_in: ReqSignIn) -> None:
        # Test sign in
        r = requests.post(f"{Settings().general.BACKEND_URL}/user/sign-in", data=req_sign_in.dict())
        response = Response(r)
        response.assert_status_code(200)
        data_model = RespSignIn(**response.response.json())
        assert data_model is not None
        assert data_model.email == req_sign_in.username


class TestBackendSession:
    def _catch_provider_requests_limit_error(self, response: Response) -> None:
        if response.response.status_code != ProviderRateLimitExceededError.status_code:
            return
        with suppress(AttributeError):
            if response.errors == ProviderRateLimitExceededError.msg:
                raise ProviderRateLimitExceededError

    @pytest.mark.dependency(depends=["TestBackendUser::test_sign_up"])
    def test_session_options(self, oauth2: OAuth2Auth) -> None:
        r = requests.get(f"{Settings().general.BACKEND_URL}/session/options", auth=oauth2)
        response = Response(r)
        self._catch_provider_requests_limit_error(response)
        response.assert_status_code(200)
        data_model = RespSessionOptions(**response.data)
        assert data_model is not None
        assert len(data_model.all_ticker) > 0
        assert data_model.all_barsnumber == [e.value for e in SessionBarsnumber]

    @pytest.mark.dependency(depends=["TestBackendUser::test_sign_up"])
    @pytest.mark.parametrize("mode", list(SessionMode))
    def test_start_new_session_custom(
        self, oauth2: OAuth2Auth, mode: SessionMode, req_session_params_custom: ReqSession
    ) -> None:
        r = requests.post(
            f"{Settings().general.BACKEND_URL}/session/{mode.value}",
            data=req_session_params_custom.json() if mode == SessionMode.custom else None,
            auth=oauth2,
        )
        response = Response(r)
        self._catch_provider_requests_limit_error(response)
        response.assert_status_code(200)
