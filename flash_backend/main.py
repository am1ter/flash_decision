import uvicorn
from fastapi import FastAPI

from app import logger, settings, uvicorn_log_config

fastapi_app = FastAPI(title="Flash decision")


@fastapi_app.on_event("startup")
async def event_startup() -> None:
    logger.info("Application ready for startup")


@fastapi_app.on_event("shutdown")
async def event_shutdown() -> None:
    logger.info("Application shutting down")


if __name__ == "__main__":
    if settings.ENVIRONMENT == "development":
        uvicorn.run(
            "main:fastapi_app",
            port=settings.PORT_BACKEND,
            reload=True,
            reload_dirs=[settings.WORK_DIR],
            log_config=uvicorn_log_config,
        )
    else:
        uvicorn.run(
            "main:fastapi_app",
            port=settings.PORT_BACKEND,
            log_config=uvicorn_log_config,
        )
