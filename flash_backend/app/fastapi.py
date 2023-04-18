from fastapi import FastAPI

from .logger import logger, settings
from .api.support import router as router_support


fastapi_app = FastAPI(title="Flash decision")
fastapi_app.include_router(router_support)


@fastapi_app.on_event("startup")
async def event_startup() -> None:
    logger.info(f"Application ready for startup", env=settings.ENVIRONMENT)


@fastapi_app.on_event("shutdown")
async def event_shutdown() -> None:
    logger.info("Application is shutting down")
