from typing import Literal
from pydantic import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: Literal["development", "production"] = "development"


settings = Settings()
