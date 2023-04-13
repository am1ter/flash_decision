from typing import Literal

from pydantic import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: Literal["development", "production"] = "development"
    WORK_DIR: str = "./flash_backend"
    URL_BACKEND: str = "http://localhost:8001/api/v1"
    PORT_BACKEND: int = 8001


settings = Settings()
