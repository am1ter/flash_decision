import os
from unittest import TestCase, mock

from app.system.config import settings_general
from app.system.exceptions import ConfigHTTPInconsistentError, ConfigHTTPWrongURLError

# Vars for patching env vars using `@mock.patch.dict` decorator
wrong_backend_url = {"BACKEND_URL": "localhost"}
inconsistent_backend_url = {"BACKEND_URL": "http://0.0.0.0:8001/api"}


class TestSettingsGeneral(TestCase):
    """Test reading and processing key settings of the app"""

    @mock.patch.dict(os.environ, wrong_backend_url)
    def test_backend_url_validation_wrong(self) -> None:
        settings_general.BACKEND_HOST = "localhost"
        with self.assertRaises(ConfigHTTPWrongURLError) as e:
            self.assertEqual(settings_general.BACKEND_URL, wrong_backend_url["BACKEND_URL"])
        self.assertEqual(type(e.exception), ConfigHTTPWrongURLError, "Wrong URL does not catched")

    @mock.patch.dict(os.environ, inconsistent_backend_url)
    def test_backend_url_validation_inconsistent(self) -> None:
        settings_general.BACKEND_HOST = "localhost"
        with self.assertRaises(ConfigHTTPInconsistentError) as e:
            self.assertEqual(settings_general.BACKEND_URL, inconsistent_backend_url["BACKEND_URL"])
        self.assertEqual(
            type(e.exception), ConfigHTTPInconsistentError, "Inconsistency does not catched"
        )
