from typing import Literal

from pydantic import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: Literal["development", "production"] = "development"
    WORK_DIR: str = "./flash_backend"
    URL_BACKEND: str = "127.0.0.1"
    PORT_BACKEND: int = 8001


settings = Settings()
