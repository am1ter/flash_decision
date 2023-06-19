import pytest

from app.system.config import settings_general
from app.system.exceptions import ConfigHTTPHardcodedBackendUrlError, ConfigHTTPWrongURLError


@pytest.fixture()
def _mock_env_hardcode_backend_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BACKEND_URL", "http://0.0.0.0:8001/api")


@pytest.fixture()
def _mock_settings_wrong_backend_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings_general, "BACKEND_HOST", ".localhost")


class TestSettingsGeneral:
    """Test reading and processing key settings of the app"""

    @pytest.mark.usefixtures("_mock_settings_wrong_backend_host")
    def test_backend_url_validation_wrong(self) -> None:
        with pytest.raises(ConfigHTTPWrongURLError):
            assert isinstance(settings_general.BACKEND_URL, str)

    @pytest.mark.usefixtures("_mock_env_hardcode_backend_url")
    def test_backend_url_hardcoded_env_var(self) -> None:
        with pytest.raises(ConfigHTTPHardcodedBackendUrlError):
            assert isinstance(settings_general.BACKEND_URL, str)
