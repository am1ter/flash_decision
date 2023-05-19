import uvicorn

from app.api.fastapi import fastapi_app
from app.system.config import settings
from app.system.logger import uvicorn_log_config

if __name__ == "__main__":
    if settings.DEV_MODE:
        uvicorn.run(
            "app.api.fastapi:fastapi_app",
            host=settings.BACKEND_HOST,
            port=settings.BACKEND_PORT,
            reload=True,
            reload_dirs=["flash_backend/app"],
            log_config=uvicorn_log_config,
        )
    else:
        uvicorn.run(
            fastapi_app,
            host=settings.BACKEND_HOST,
            port=settings.BACKEND_PORT,
            log_config=uvicorn_log_config,
        )
