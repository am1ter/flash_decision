from pydantic import BaseSettings, PostgresDsn

from .constants import Environment


class SettingsGeneral(BaseSettings):
    # Env
    ENVIRONMENT: Environment = Environment.development
    DEV_MODE: bool = bool(ENVIRONMENT == Environment.development)
    WORK_DIR: str = "./flash_backend"
    # HTTP
    URL_BACKEND: str = "http://localhost:8001/api/v1"
    PORT_BACKEND: int = 8001


settings_general = SettingsGeneral()


class SettingsLog(BaseSettings):
    LOG_DB_ACCESS: bool = bool(settings_general.DEV_MODE)
    LOG_FMT_DEV_PREF: str = "%(asctime)s [%(levelprefix)s]"
    LOG_FMT_DEV_DEFAULT: str = LOG_FMT_DEV_PREF + " %(message)s"
    LOG_FMT_DEV_ACCESS: str = (
        LOG_FMT_DEV_PREF + " %(client_addr)s | %(request_line)s | %(status_code)s"
    )


settings_log = SettingsLog()


class SettingsDb(BaseSettings):
    DB_ENGINE_SCHEMA: str = "postgresql+asyncpg"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "flash!Pass"
    DB_NAME: str = "flash_decision"
    DB_SCHEMA: str = settings_general.ENVIRONMENT.value
    DB_URL: str = PostgresDsn.build(
        scheme=DB_ENGINE_SCHEMA,
        host=DB_HOST,
        port=str(DB_PORT),
        user=DB_USER,
        password=DB_PASS,
        path=f"/{DB_NAME}",
    )


settings_db = SettingsDb()


class Settings(SettingsGeneral, SettingsLog, SettingsDb):
    pass


settings = Settings()
