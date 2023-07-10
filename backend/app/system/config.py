import os
from copy import copy
from distutils.util import strtobool
from functools import cached_property
from typing import Literal

from pydantic import BaseSettings, HttpUrl, PostgresDsn, RedisDsn, ValidationError, parse_obj_as

from app.system.constants import Environment
from app.system.exceptions import ConfigHTTPHardcodedBackendUrlError, ConfigHTTPWrongURLError


class BaseSettingsCustom(BaseSettings):
    """Parent class for all settings subclasses"""

    class Config:
        # Allow use cached_property
        keep_untouched = (cached_property,)


class SettingsGeneral(BaseSettingsCustom):
    # Env
    ENVIRONMENT: Environment = Environment.production
    # HTTP
    BACKEND_PROTOCOL: Literal["http", "https"] = "http"
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 8001
    BACKEND_API_PREFIX: str = "api/v1"
    FRONTEND_URL: str = "http://0.0.0.0:8000/"
    # JWT
    JWT_SECRET_KEY: str = "my_jwt_secret_key"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    JWT_ALGORITHM: str = "HS256"

    @cached_property
    def BACKEND_URL(self) -> str:  # noqa: N802
        if os.getenv("BACKEND_URL"):
            raise ConfigHTTPHardcodedBackendUrlError

        # Constuct url
        url_base = f"{self.BACKEND_PROTOCOL}://{self.BACKEND_HOST}:{self.BACKEND_PORT!s}"
        url_api = f"{url_base}/{self.BACKEND_API_PREFIX}"
        url_api = url_api.lower()

        # Parse URL and validate it
        try:
            # Allow urls without `top level domain` like `localhost`
            http_url_no_tld = copy(HttpUrl)
            http_url_no_tld.tld_required = False
            parse_obj_as(http_url_no_tld, url_api)
        except ValidationError as e:
            raise ConfigHTTPWrongURLError from e

        return url_api

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
    SUPPRESS_TRACEBACK_FROM_LIBS: tuple[str, ...] = (
        "uvicorn",
        "fastapi",
        "starlette",
        "sqlalchemy",
        "asyncpg",
        "attrs",
        "attr",
        "asyncio",
    )


settings_log = SettingsLog()


class SettingsDb(BaseSettingsCustom):
    DB_ENGINE_SCHEMA: str = "postgresql+asyncpg"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "my_db_pass"
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

    @cached_property
    def DB_URL_WO_PASS(self) -> str:  # noqa: N802
        return PostgresDsn.build(
            scheme=self.DB_ENGINE_SCHEMA,
            host=self.DB_HOST,
            port=str(self.DB_PORT),
            user=self.DB_USER,
            password="*****",  # noqa: S106
            path=f"/{self.DB_NAME}",
        )


settings_db = SettingsDb()


class SettingsCache(BaseSettingsCustom):
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 60 * 60 * 24  # seconds
    CACHE_REDIS_SCHEMA: str = "redis"
    CACHE_REDIS_HOST: str = "localhost"
    CACHE_REDIS_PORT: int = 6379
    CACHE_REDIS_DB: int = 0
    CACHE_REDIS_PASS: str = "my_redis_pass"
    CACHE_REDIS_DECODE_RESPONSES = True

    @cached_property
    def CACHE_REDIS_URL(self) -> str:  # noqa: N802
        return RedisDsn.build(
            scheme=self.CACHE_REDIS_SCHEMA,
            host=self.CACHE_REDIS_HOST,
            port=str(self.CACHE_REDIS_PORT),
            password=self.CACHE_REDIS_PASS,
            path=f"/{self.CACHE_REDIS_DB!s}",
        )


settings_cache = SettingsCache()


class SettingsProvider(BaseSettingsCustom):
    ALPHAVANTAGE_API_KEY = "my_alpha_avantage_api_key"
    CRYPTO_PRICE_CURRENCY = "USD"  # Source: https://www.alphavantage.co/physical_currency_list/
    RANDOM_TICKERS_STOCKS = "AMZN,META,GOOGL,AAPL,AMD,XOM,GS,DAL,NKE,NFLX,INTC,TSLA,MSFT,PEP,DIS"
    RANDOM_TICKERS_CRYPTO = "BTC,BNB,SOL,XRP,ADA,DOGE,LTC"


settings_provider = SettingsProvider()


class Settings(SettingsGeneral, SettingsLog, SettingsDb, SettingsProvider, SettingsCache):
    pass


settings = Settings()
