import uvicorn

from app.system.config import settings
from app.system.logger import update_uvicorn_log_config


def run() -> None:
    if settings.DEV_MODE:
        uvicorn.run(
            "app.api.fastapi:fastapi_app",
            host=settings.BACKEND_HOST,
            port=settings.BACKEND_PORT,
            log_config=update_uvicorn_log_config(),
            reload=True,
            reload_dirs=["backend/app", "app"],  # local / docker path
        )
    else:
        uvicorn.run(
            "app.api.fastapi:fastapi_app",
            host=settings.BACKEND_HOST,
            port=settings.BACKEND_PORT,
            log_config=update_uvicorn_log_config(),
        )


if __name__ == "__main__":
    run()
