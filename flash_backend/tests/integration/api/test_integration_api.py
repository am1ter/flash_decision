from __future__ import annotations

import unittest

import requests

from app.api.schemas.support import RespDataHealthcheck
from app.api.schemas.user import ReqSignIn, ReqSignUp, RespSignIn, RespSignUp
from app.system.config import settings


class Response:
    def __init__(self, response: requests.Response) -> None:
        self.response = response
        self.json = self.response.json()
        self.meta = self.json.get("meta")
        self.data = self.json.get("data")
        self.errors = self.json.get("errors")
        self.status = self.response.status_code
        self.url = self.response.url

    def __repr__(self) -> str:
        return f"<Response({self.status=}, {self.errors=}, {self.url=})>"

    def assert_status_code(self, status_code: int) -> Response:
        assert self.response.status_code == status_code, f"Wrong status code for {self}"
        return self


class TestBackendSupport(unittest.TestCase):
    def test_run_healthcheck(self) -> None:
        r = requests.get(f"{settings.BACKEND_URL}/support/healthcheck")
        response = Response(r)
        response.assert_status_code(200)
        data_model = RespDataHealthcheck(**response.data)
        self.assertIsNotNone(data_model)
        self.assertEqual(data_model.is_app_up, True)
        self.assertEqual(data_model.is_db_up, True)


class TestBackendUser(unittest.TestCase):
    def test_sign_up(self) -> None:
        user_sign_up = ReqSignUp(
            email="test-signup-integration@alekseisemenov.ru",
            name="test-signup-integration",
            password="uc8a&Q!W",  # noqa: S106
        )
        r = requests.post(f"{settings.BACKEND_URL}/user/sign-up", json=user_sign_up.dict())
        response = Response(r)
        response.assert_status_code(200)
        data_model = RespSignUp(**response.data)
        self.assertIsNotNone(data_model)
        self.assertEqual(data_model.email, user_sign_up.email)

    def test_sign_in(self) -> None:
        # Create user
        user_sign_up = ReqSignUp(
            email="test-signin-integration@alekseisemenov.ru",
            name="test-signin-integration",
            password="uc8a&Q!W",  # noqa: S106
        )
        r_sign_up = requests.post(f"{settings.BACKEND_URL}/user/sign-up", json=user_sign_up.dict())
        response_sign_up = Response(r_sign_up)
        response_sign_up.assert_status_code(200)

        # Test sign in
        user_sign_in = ReqSignIn(**user_sign_up.dict())
        r_sign_in = requests.post(f"{settings.BACKEND_URL}/user/sign-in", json=user_sign_in.dict())
        response_sign_in = Response(r_sign_in)
        response_sign_in.assert_status_code(200)
        data_model = RespSignIn(**response_sign_in.data)
        self.assertIsNotNone(data_model)
        self.assertEqual(data_model.email, user_sign_in.email)
