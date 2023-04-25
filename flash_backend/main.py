import uvicorn

from app.config import settings
from app.fastapi import fastapi_app
from app.logger import uvicorn_log_config

if __name__ == "__main__":
    if settings.DEV_MODE:
        uvicorn.run(
            "app.fastapi:fastapi_app",
            port=settings.PORT_BACKEND,
            reload=True,
            reload_dirs=[settings.WORK_DIR],
            log_config=uvicorn_log_config,
        )
    else:
        uvicorn.run(
            fastapi_app,
            port=settings.PORT_BACKEND,
            log_config=uvicorn_log_config,
        )
