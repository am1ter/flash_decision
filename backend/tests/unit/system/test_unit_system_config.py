import pytest

from app.bootstrap import Bootstrap
from app.system.config import Settings
from app.system.exceptions import ConfigHTTPHardcodedBackendUrlError, ConfigHTTPWrongURLError


@pytest.fixture()
def _mock_env_hardcode_backend_url(monkeypatch: pytest.MonkeyPatch) -> None:
    type(Bootstrap)._instances = {}
    monkeypatch.setenv("BACKEND_URL", "http://0.0.0.0:8001/api")


@pytest.fixture()
def _mock_settings_wrong_backend_host(monkeypatch: pytest.MonkeyPatch) -> None:
    type(Bootstrap)._instances = {}
    monkeypatch.setattr(Settings().general, "BACKEND_HOST", ".localhost")


class TestSettingsGeneral:
    """Test reading and processing key settings of the app"""

    @pytest.mark.usefixtures("_mock_settings_wrong_backend_host")
    def test_backend_url_validation_wrong(self) -> None:
        with pytest.raises(ConfigHTTPWrongURLError):
            assert isinstance(Settings().general.BACKEND_URL, str)

    @pytest.mark.usefixtures("_mock_env_hardcode_backend_url")
    def test_backend_url_hardcoded_env_var(self) -> None:
        with pytest.raises(ConfigHTTPHardcodedBackendUrlError):
            assert isinstance(Settings().general.BACKEND_URL, str)
