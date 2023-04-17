from __future__ import annotations

import unittest

import requests

from flash_backend.app.schemas.support import RespDataHealthcheck
from flash_backend.app.config import settings


class Response:
    def __init__(self, response: requests.Response) -> None:
        self.response = response
        self.json = self.response.json()
        self.meta = self.json.get("meta")
        self.data = self.json.get("data")

    def assert_status_code(self, status_code: int) -> Response:
        assert self.response.status_code == status_code
        return self


class TestBackend(unittest.TestCase):
    def test_healthcheck(self) -> None:
        r = requests.get(f"{settings.URL_BACKEND}/support/healthcheck")
        response = Response(r)
        response.assert_status_code(200)
        data_model = RespDataHealthcheck(**response.data)
        self.assertIsNotNone(data_model)
        self.assertEqual(data_model.isAppUp, True)
