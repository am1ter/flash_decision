from fastapi import FastAPI

from .api.support import router as router_support
from .db import engine
from .logger import logger, settings

fastapi_app = FastAPI(title="Flash decision")
fastapi_app.include_router(router_support)


@fastapi_app.on_event("startup")
async def event_startup() -> None:
    logger.info(f"Application ready for startup", env=settings.ENVIRONMENT.value)
    logger.info(
        f"Connection to db established",
        db_url=engine.engine.url,
        db_schema=settings.DB_SCHEMA,
    )


@fastapi_app.on_event("shutdown")
async def event_shutdown() -> None:
    logger.info("Application is shutting down")
