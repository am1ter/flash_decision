from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status

from app.api.endpoints.session import router as router_session
from app.api.endpoints.support import router as router_support
from app.api.endpoints.user import router as router_user
from app.bootstrap import Bootstrap
from app.system.exceptions import BaseHTTPError
from app.system.logger import create_logger, settings

# Create logger
logger = create_logger("backend.fastapi")

# Run boostrap
Bootstrap(start_orm=True)

# Set up FastApi
fastapi_app = FastAPI(title="Flash decision")
fastapi_app.include_router(router_support)
fastapi_app.include_router(router_user)
fastapi_app.include_router(router_session)
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@fastapi_app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Format exceptions in a `JSON:API` specification style using info from custom exceptions"""
    if isinstance(exc, BaseHTTPError):
        return JSONResponse(
            status_code=exc.status_code, content={"errors": exc.msg}, headers=exc.headers
        )
    else:
        exc_name = type(exc).__name__
        try:
            exc_desc = str(exc)
        except AttributeError:
            if isinstance(exc, ValidationError):
                exc_desc = "Pydantic response model validation error"
            else:
                exc_desc = "Unknown error"
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errors": f"{exc_name}: {exc_desc}"},
        )


@fastapi_app.on_event("startup")
async def event_startup() -> None:
    await logger.ainfo(
        f"Application ready for startup",
        env=settings.ENVIRONMENT.value,
        dev_mode=settings.DEV_MODE,
        debug_mode=settings.DEBUG_MODE,
    )
    await logger.ainfo(
        f"Connection to db established",
        db_url=settings.DB_URL_WO_PASS,
        db_schema=settings.DB_SCHEMA,
    )


@fastapi_app.on_event("shutdown")
async def event_shutdown() -> None:
    await logger.ainfo("Application is shutting down")
