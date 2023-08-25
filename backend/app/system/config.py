import os
from distutils.util import strtobool
from functools import cached_property
from typing import Literal

from pydantic import HttpUrl, MongoDsn, PostgresDsn, RedisDsn, TypeAdapter, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.system.constants import Environment
from app.system.exceptions import ConfigHTTPHardcodedBackendUrlError, ConfigHTTPWrongURLError
from app.system.metaclasses import SingletonMeta


class BaseSettingsCustom(BaseSettings):
    """Parent class for all settings subclasses"""

    model_config = SettingsConfigDict(ignored_types=(cached_property,))  # Allow use cached_property


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
    # Scoreboard
    TOP_USER_COUNT: int = 3

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
            TypeAdapter(HttpUrl).validate_python(url_api)
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


class SettingsLog(BaseSettingsCustom):
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_SQL_ACCESS: bool = SettingsGeneral().DEBUG_MODE
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
        "pandas",
        "pymongo",
    )


class SettingsDbSql(BaseSettingsCustom):
    SQL_ENGINE_SCHEMA: str = "postgresql+asyncpg"
    SQL_HOST: str = "localhost"
    SQL_PORT: int = 5432
    SQL_USER: str = "postgres"
    SQL_PASS: str = "my_sql_pass"
    SQL_DB_NAME: str = "flash_decision"
    SQL_DB_SCHEMA: str = SettingsGeneral().ENVIRONMENT.value

    @cached_property
    def SQL_URL(self) -> str:  # noqa: N802
        url = PostgresDsn.build(
            scheme=self.SQL_ENGINE_SCHEMA,
            host=self.SQL_HOST,
            port=self.SQL_PORT,
            username=self.SQL_USER,
            password=self.SQL_PASS,
            path=f"{self.SQL_DB_NAME}",
        )
        return str(url)

    @cached_property
    def SQL_URL_WO_PASS(self) -> str:  # noqa: N802
        return self.SQL_URL.replace(self.SQL_PASS, "***")


class SettingsDbNoSql(BaseSettingsCustom):
    NOSQL_ENGINE_SCHEMA: str = "mongodb"
    NOSQL_HOST: str = "localhost"
    NOSQL_PORT: int = 27017
    NOSQL_USER: str = "root"
    NOSQL_PASS: str = "my_mongo_pass"
    NOSQL_DB_NAME: str = SettingsGeneral().ENVIRONMENT.value

    @cached_property
    def NOSQL_URL(self) -> str:  # noqa: N802
        url = MongoDsn.build(
            scheme=self.NOSQL_ENGINE_SCHEMA,
            host=self.NOSQL_HOST,
            port=self.NOSQL_PORT,
            username=self.NOSQL_USER,
            password=self.NOSQL_PASS,
        )
        return str(url)

    @cached_property
    def NOSQL_URL_WO_PASS(self) -> str:  # noqa: N802
        return self.NOSQL_URL.replace(self.NOSQL_PASS, "***")


class SettingsCache(BaseSettingsCustom):
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 60 * 60 * 24  # seconds
    CACHE_REDIS_SCHEMA: str = "redis"
    CACHE_REDIS_HOST: str = "localhost"
    CACHE_REDIS_PORT: int = 6379
    CACHE_REDIS_DB: int = 0
    CACHE_REDIS_PASS: str = "my_redis_pass"
    CACHE_REDIS_DECODE_RESPONSES: bool = True

    @cached_property
    def CACHE_REDIS_URL(self) -> str:  # noqa: N802
        url = RedisDsn.build(
            scheme=self.CACHE_REDIS_SCHEMA,
            host=self.CACHE_REDIS_HOST,
            port=self.CACHE_REDIS_PORT,
            password=self.CACHE_REDIS_PASS,
            path=f"{self.CACHE_REDIS_DB!s}",
        )
        return str(url)


class SettingsProvider(BaseSettingsCustom):
    ALPHAVANTAGE_API_KEY_STOCKS: str = "my_alpha_avantage_api_key"
    ALPHAVANTAGE_API_KEY_CRYPTO: str = "my_alpha_avantage_api_key"
    CRYPTO_PRICE_CURRENCY: str = "CNY"  # Source: https://www.alphavantage.co/physical_currency_list
    RANDOM_TICKERS_STOCKS: str = "AMZN,META,GOOGL,AAPL,AMD,XOM,GS,DAL,NKE,NFLX,INTC,TSLA,MSFT,PEP"
    RANDOM_TICKERS_CRYPTO: str = "BTC,BNB,ETH,DOGE,MATIC,BCH"


class Settings(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.general = SettingsGeneral()
        self.log = SettingsLog()
        self.sql = SettingsDbSql()
        self.nosql = SettingsDbNoSql()
        self.provider = SettingsProvider()
        self.cache = SettingsCache()
