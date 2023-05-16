from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from app.api.endpoints.support import router as router_support
from app.api.endpoints.user import router as router_user
from app.system.exceptions import BaseHTTPError
from app.system.logger import logger, settings

fastapi_app = FastAPI(title="Flash decision")
fastapi_app.include_router(router_support)
fastapi_app.include_router(router_user)


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
        db_url=settings.DB_URL,
        db_schema=settings.DB_SCHEMA,
    )


@fastapi_app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Format exceptions in a `JSON:API` specification style using info from custom exceptions"""
    if isinstance(exc, BaseHTTPError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"errors": exc.msg},
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errors": f"{type(exc).__name__}: {exc!s}"},
        )


@fastapi_app.on_event("shutdown")
async def event_shutdown() -> None:
    logger.info("Application is shutting down")
