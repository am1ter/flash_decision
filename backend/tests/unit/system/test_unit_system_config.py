import os
from unittest import TestCase, mock

from app.system.config import settings_general
from app.system.exceptions import ConfigHTTPHardcodedBackendUrlError, ConfigHTTPWrongURLError

# Vars for patching env vars using `@mock.patch.dict` decorator
hardcoded_backend_url = {"BACKEND_URL": "http://0.0.0.0:8001/api"}


class TestSettingsGeneral(TestCase):
    """Test reading and processing key settings of the app"""

    def test_backend_url_validation_wrong(self) -> None:
        settings_general.BACKEND_HOST = ".localhost"
        with self.assertRaises(ConfigHTTPWrongURLError):
            self.assertTrue(isinstance(settings_general.BACKEND_URL, str))

    @mock.patch.dict(os.environ, hardcoded_backend_url)
    def test_backend_url_hardcoded_env_var(self) -> None:
        with self.assertRaises(ConfigHTTPHardcodedBackendUrlError):
            self.assertTrue(isinstance(settings_general.BACKEND_URL, str))
