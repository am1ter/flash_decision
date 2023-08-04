from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status

from app.api.endpoints.session import router as router_session
from app.api.endpoints.session_decision import router as router_decision
from app.api.endpoints.session_iteration import router as router_iteration
from app.api.endpoints.support import router as router_support
from app.api.endpoints.user import router as router_user
from app.system.config import Settings
from app.system.exceptions import BaseHTTPError

# Create logger
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator:
    logger.info(
        "Startup finished",
        env=Settings().general.ENVIRONMENT.value,
        dev_mode=Settings().general.DEV_MODE,
        debug_mode=Settings().general.DEBUG_MODE,
    )
    yield
    await logger.ainfo("Application is shutting down")


# Set up FastApi
fastapi_app = FastAPI(lifespan=lifespan, title="Flash decision")
fastapi_app.include_router(router_support)
fastapi_app.include_router(router_user)
fastapi_app.include_router(router_session)
fastapi_app.include_router(router_iteration)
fastapi_app.include_router(router_decision)
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[Settings().general.FRONTEND_URL],
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
