import unittest

import requests as r

import unit.config as cfg


class TestBackend(unittest.TestCase):
    def test_healthcheck(self) -> None:
        request = r.get(f"{cfg.URL_BACKEND}/support/healthcheck")
        assert request.status_code == 200
