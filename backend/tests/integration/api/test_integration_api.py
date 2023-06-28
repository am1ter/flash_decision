from __future__ import annotations

import pytest
import requests
from requests import JSONDecodeError

from app.api.schemas.support import RespDataHealthcheck
from app.api.schemas.user import ReqSignIn, ReqSignUp, RespSignIn, RespSignUp
from app.system.config import settings


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
        except JSONDecodeError:
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
        base_url = (
            f"{settings.BACKEND_PROTOCOL}://{settings.BACKEND_HOST}:{settings.BACKEND_PORT!s}"
        )
        r = requests.get(f"{base_url}/docs")
        response = Response(r)
        response.assert_status_code(200)


class TestBackendSupport:
    def test_run_healthcheck(self) -> None:
        r = requests.get(f"{settings.BACKEND_URL}/support/healthcheck")
        response = Response(r)
        response.assert_status_code(200)
        data_model = RespDataHealthcheck(**response.data)
        assert data_model is not None
        assert data_model.is_app_up
        assert data_model.is_db_up


class TestBackendUser:
    @pytest.mark.dependency()
    def test_sign_up(self, req_sign_up: ReqSignUp) -> None:
        r = requests.post(f"{settings.BACKEND_URL}/user/sign-up", json=req_sign_up.dict())
        response = Response(r)
        response.assert_status_code(200)
        data_model = RespSignUp(**response.response.json())
        assert data_model is not None
        assert data_model.email == req_sign_up.email

    @pytest.mark.dependency(depends=["TestBackendUser::test_sign_up"])
    def test_sign_in(self, req_sign_in: ReqSignIn) -> None:
        # Test sign in
        r = requests.post(f"{settings.BACKEND_URL}/user/sign-in", data=req_sign_in.dict())
        response = Response(r)
        response.assert_status_code(200)
        data_model = RespSignIn(**response.response.json())
        assert data_model is not None
        assert data_model.email == req_sign_in.username
