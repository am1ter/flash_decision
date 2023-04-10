import unittest

import requests as r

import unit.config as cfg


class TestBackend(unittest.TestCase):
    def test_healthcheck(self) -> None:
        request = r.get(cfg.URL_BACKEND)
        assert request.status_code == 200
