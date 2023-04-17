from typing import Literal

from pydantic import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: Literal["development", "production"] = "development"
    WORK_DIR: str = "./flash_backend"
    URL_BACKEND: str = "http://localhost:8001/api/v1"
    PORT_BACKEND: int = 8001
    LOG_FMT_DEV_PREF = "%(asctime)s [%(levelprefix)s]"
    LOG_FMT_DEV_DEFAULT = LOG_FMT_DEV_PREF + " %(message)s"
    LOG_FMT_DEV_ACCESS = LOG_FMT_DEV_PREF + " %(client_addr)s | %(request_line)s | %(status_code)s"


settings = Settings()
