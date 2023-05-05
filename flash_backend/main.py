import uvicorn

from app.api.fastapi import fastapi_app
from app.system.config import settings
from app.system.logger import uvicorn_log_config

if __name__ == "__main__":
    if settings.DEV_MODE:
        uvicorn.run(
            "app.api.fastapi:fastapi_app",
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
