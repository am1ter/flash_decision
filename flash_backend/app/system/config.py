import os
from distutils.util import strtobool
from functools import cached_property

from pydantic import BaseSettings, PostgresDsn

from app.system.constants import Environment


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

    @cached_property
    def BACKEND_URL(self) -> str:  # noqa: N802
        backend_url_from_env = os.getenv("BACKEND_URL")
        if backend_url_from_env:
            return backend_url_from_env
        else:
            return f"http://{self.BACKEND_HOST}:{self.BACKEND_PORT!s}/api/v1"

    @cached_property
    def DEV_MODE(self) -> bool:  # noqa: N802
        return self.ENVIRONMENT == Environment.development

    @cached_property
    def DEBUG_MODE(self) -> bool:  # noqa: N802
        if self.DEV_MODE and bool(strtobool(os.getenv("DEBUG_MODE", default="False"))):
            os.environ["PYTHONASYNCIODEBUG"] = "1"
            return True
        return False


settings_general = SettingsGeneral()


class SettingsLog(BaseSettingsCustom):
    LOG_DB_ACCESS: bool = settings_general.DEBUG_MODE
    LOG_FMT_DEV_PREF: str = "%(asctime)s [%(levelprefix)s]"
    LOG_FMT_DEV_DEFAULT: str = LOG_FMT_DEV_PREF + " %(message)s"
    LOG_FMT_DEV_ACCESS: str = (
        LOG_FMT_DEV_PREF + " %(client_addr)s | %(request_line)s | %(status_code)s"
    )
    SUPPRESS_TRACEBACK_FROM_LIBS = [
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
