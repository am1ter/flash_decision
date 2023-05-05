from fastapi import FastAPI

from app.api.endpoints.support import router as router_support
from app.infrastructure.db import engine
from app.system.logger import logger, settings

fastapi_app = FastAPI(title="Flash decision")
fastapi_app.include_router(router_support)


@fastapi_app.on_event("startup")
async def event_startup() -> None:
    logger.info(
        f"Application ready for startup",
        env=settings.ENVIRONMENT.value,
        dev_mode=settings.DEV_MODE,
        debug_mode=settings.DEBUG_MODE,
    )
    logger.info(
        f"Connection to db established",
        db_url=engine.engine.url,
        db_schema=settings.DB_SCHEMA,
    )


@fastapi_app.on_event("shutdown")
async def event_shutdown() -> None:
    logger.info("Application is shutting down")
