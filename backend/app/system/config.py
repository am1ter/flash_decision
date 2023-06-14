import os
from copy import copy
from distutils.util import strtobool
from functools import cached_property
from typing import Literal

from pydantic import BaseSettings, HttpUrl, PostgresDsn, ValidationError, parse_obj_as

from app.system.constants import Environment
from app.system.exceptions import ConfigHTTPInconsistentError, ConfigHTTPWrongURLError


class BaseSettingsCustom(BaseSettings):
    """Parent class for all settings subclasses"""

    class Config:
        # Allow use cached_property
        keep_untouched = (cached_property,)


class SettingsGeneral(BaseSettingsCustom):
    # Env
    ENVIRONMENT: Environment = Environment.production
    # HTTP
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 8001
    FRONTEND_URL: str = "http://0.0.0.0:8000/"
    # JWT
    JWT_SECRET_KEY: str = "fff76ea4d26ce6fd5390f79d478cb8a4"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"

    @cached_property
    def BACKEND_URL(self) -> str:  # noqa: N802
        backend_url_from_env = os.getenv("BACKEND_URL")

        # If backend url is not set up create it dynamically
        if not backend_url_from_env:
            return f"http://{self.BACKEND_HOST}:{self.BACKEND_PORT!s}/api/v1"

        # Parse URL and validate it
        try:
            # Allow urls without `top level domain` like `localhost`
            http_url_no_tld = copy(HttpUrl)
            http_url_no_tld.tld_required = False
            backend_url_from_env_obj = parse_obj_as(http_url_no_tld, backend_url_from_env)
        except ValidationError as e:
            raise ConfigHTTPWrongURLError from e

        # Check if backend_url and backend_host are consistent with each other
        if backend_url_from_env_obj.host.lower() != self.BACKEND_HOST:
            raise ConfigHTTPInconsistentError

        return backend_url_from_env

    @cached_property
    def DEV_MODE(self) -> bool:  # noqa: N802
        os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"
        return self.ENVIRONMENT == Environment.development

    @cached_property
    def DEBUG_MODE(self) -> bool:  # noqa: N802
        if self.DEV_MODE and bool(strtobool(os.getenv("DEBUG_MODE", default="False"))):
            os.environ["PYTHONASYNCIODEBUG"] = "1"
            return True
        return False


settings_general = SettingsGeneral()


class SettingsLog(BaseSettingsCustom):
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_DB_ACCESS: bool = settings_general.DEBUG_MODE
    LOG_FMT_DEV_PREF: str = "%(asctime)s [%(levelprefix)s]"
    LOG_FMT_DEV_DEFAULT: str = LOG_FMT_DEV_PREF + " %(message)s"
    LOG_FMT_DEV_ACCESS: str = (
        LOG_FMT_DEV_PREF + " %(client_addr)s | %(request_line)s | %(status_code)s"
    )
    SUPPRESS_TRACEBACK_FROM_LIBS: list[str] = [
        "uvicorn",
        "fastapi",
        "starlette",
        "sqlalchemy",
        "asyncpg",
        "attrs",
        "attr",
        "asyncio",
    ]


settings_log = SettingsLog()


class SettingsDb(BaseSettingsCustom):
    DB_ENGINE_SCHEMA: str = "postgresql+asyncpg"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "flash!Pass"
    DB_NAME: str = "flash_decision"
    DB_SCHEMA: str = settings_general.ENVIRONMENT.value

    @cached_property
    def DB_URL(self) -> str:  # noqa: N802
        return PostgresDsn.build(
            scheme=self.DB_ENGINE_SCHEMA,
            host=self.DB_HOST,
            port=str(self.DB_PORT),
            user=self.DB_USER,
            password=self.DB_PASS,
            path=f"/{self.DB_NAME}",
        )


settings_db = SettingsDb()


class Settings(SettingsGeneral, SettingsLog, SettingsDb):
    pass


settings = Settings()
