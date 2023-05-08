import logging
import re
import sys
import traceback
from copy import deepcopy
from datetime import datetime
from logging import LogRecord
from types import TracebackType
from typing import Any, Literal

import asyncpg
import attrs
import fastapi
import sqlalchemy
import starlette
import structlog
import uvicorn
from rich import print as rprint
from rich.traceback import Traceback
from structlog.stdlib import LoggerFactory
from structlog.typing import EventDict
from uvicorn.config import LOGGING_CONFIG
from uvicorn.logging import AccessFormatter, DefaultFormatter

from app.system.config import settings


def rich_excepthook(
    type_: type[BaseException], value: BaseException, traceback: TracebackType | None
) -> None:
    """Format exception using rich lib"""
    rich_tb = Traceback.from_exception(
        type_,
        value,
        traceback,
        show_locals=True,
        suppress=[uvicorn, fastapi, starlette, sqlalchemy, asyncpg, attrs],
    )
    rprint(rich_tb)


class UvicornCustomDefaultFormatter(DefaultFormatter):
    """Custom unicorn logger for system messages"""

    def __init__(  # noqa: PLR0913
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool | None = None,
        custom_logger: structlog.stdlib.BoundLogger | None = None,
        dev_mode: bool | None = None,
    ) -> None:
        """Change format for Uvicorn logs to unify it with structlog format"""

        # Source record has format like: [\x1b[32mINFO\x1b[0m:    ]
        self.regex_level = re.compile(r"[0-9]{1,2}m.*[0-9]{1,2}m:")
        self.tags_escape = re.compile(r"\x1b\[([0-9]{1,2})[m]")
        super().__init__(fmt, datefmt, style, use_colors)

        # Force setup dev_mode
        self.dev_mode = dev_mode

        # Custom logger could be used only for formatting exception
        self.logger = custom_logger if custom_logger else logger

    def formatException(  # type: ignore[override]  # noqa: N802
        self, ei: tuple[type[BaseException], BaseException, TracebackType | None]
    ) -> None:
        """Override exception formatting for uvicorn"""
        if self.dev_mode or settings.DEV_MODE:
            # Use rich print which support suppressing external lib attributes
            rich_excepthook(ei[0], ei[1], ei[2])
        else:
            self.logger.exception(str(ei[1]), exc_info=ei)

    def formatMessage(self, record: LogRecord) -> str:  # noqa: N802
        """Override default formatting method for system logs"""
        record_source = super().formatMessage(record)
        if self.dev_mode or settings.DEV_MODE:
            # Reformat level
            try:
                level_raw = self.regex_level.findall(record_source)[0]
            except IndexError:
                return record_source
            level_new = level_raw.lower().replace(":", " ")
            # Update record
            record_new = self.regex_level.sub(level_new, record_source)
            return record_new
        else:
            record_new_as_dict = {
                "logger": record.name,
                "event": record.message,
                "level": record.levelname.lower(),
                "level_number": record.levelno,
                "timestamp": record.asctime,
            }
            return str(record_new_as_dict)


class UvicornCustomFormatterAccess(AccessFormatter):
    """Custom unicorn logger for access messages"""

    def __init__(  # noqa: PLR0913
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool | None = None,
        dev_mode: bool | None = None,
    ) -> None:
        """
        Final access message is a combination of formatted prefix and formatted raw access message
        Prefix formatted with UvicornCustomDefaultFormatter
        """
        fmt_access = fmt.replace(settings.LOG_FMT_DEV_PREF, "") if fmt else None
        self.default_formatter = UvicornCustomDefaultFormatter(
            fmt=settings.LOG_FMT_DEV_PREF, dev_mode=dev_mode
        )
        self.access_formatter = AccessFormatter(fmt_access)
        super().__init__(fmt, datefmt, style, use_colors)

        # Force setup dev_mode
        self.dev_mode = dev_mode

    def formatMessage(self, record: LogRecord) -> str:  # noqa: N802
        """Override default formatting method for access logs"""
        record_default = self.default_formatter.formatMessage(record)
        record_access = self.access_formatter.formatMessage(record)
        if self.dev_mode or settings.DEV_MODE:
            return record_default + record_access
        else:
            if record.args and len(record.args) == 5:
                access_args = [arg for arg in record.args if arg]
            else:
                # Extra verification, incl. because of the mypy requirements.
                raise RuntimeError(f"Wrong access arguments for {record=}")
            record_new_as_dict = {
                "logger": record.name,
                "event": record.message,
                "level": record.levelname.lower(),
                "level_number": record.levelno,
                "timestamp": record.asctime,
                "client_addr": access_args[0],
                "method": access_args[1],
                "full_path": access_args[2],
                "http_version": access_args[3],
                "status_code": access_args[4],
            }
            return str(record_new_as_dict)


class CustomTimeStamper(structlog.processors.TimeStamper):
    """Reformat logs from structlog to contain miliseconds (3 digit fraction)"""

    def __init__(self, fmt: str | None, *, key: str = "timestamp", utc: bool = False) -> None:
        super().__init__(fmt=fmt, key=key, utc=utc)

    def __call__(
        self, logger: structlog.stdlib.BoundLogger, name: str, event_dict: EventDict
    ) -> EventDict:
        time_func = datetime.utcnow if self.utc else datetime.now
        event_dict[self.key] = time_func().strftime(self.fmt)[:-3]  # type: ignore[operator]
        return event_dict


class CustomStructlogLogger(structlog.stdlib.BoundLogger):
    """Custom structlog logger with additional methods and other tweaks"""

    def info(self, event: str | None = None, *args: Any, **kw: Any) -> Any:
        """Custom wrapper for logger method"""
        # Show class name
        if kw.get("cls") and isinstance(kw.get("cls"), type):
            kw["cls"] = kw["cls"].__name__

        # Show the name of the function, where info() called
        if kw.get("show_func_name", False):
            del kw["show_func_name"]
            callstack_depth = 3
            kw["function"] = traceback.extract_stack(None, callstack_depth)[0].name

        # Output to logger
        return self._logger.info(event, *args, **kw)

    def info_finish(self, *args, **kw) -> None:
        """To log function/method results"""
        event = "Operation completed"
        self.info(event, *args, **kw)

    def exception(self, event: str | None = None, *args: Any, **kw: Any) -> Any:
        """Use parent logger of wrapped custom logger"""
        return self._logger.exception(event, *args, **kw)


def create_logger(
    logger_name: str | None = None, dev_mode: bool | None = None
) -> CustomStructlogLogger:
    """Create structlog logger"""

    # Set log level and remove extra data from output using format argument
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)

    # Configure structlog
    processors_shared: list = [
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        CustomTimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=False),
    ]
    processors_mode: list[Any]
    if dev_mode or settings.DEV_MODE:
        processors_mode = [
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        # Setup processors
        processors_mode = [
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level_number,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    structlog.configure(
        processors=processors_shared + processors_mode,
        cache_logger_on_first_use=True,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
    )
    logger = structlog.get_logger(logger_name) if logger_name else structlog.get_logger()
    return structlog.wrap_logger(logger, wrapper_class=CustomStructlogLogger)


def update_uvicorn_log_config() -> dict[str, Any]:
    """Change uvicorn log settings to conform with structlog"""

    uvicorn_log_config = deepcopy(LOGGING_CONFIG)
    uvicorn_log_config["formatters"]["custom_default"] = {
        "()": UvicornCustomDefaultFormatter,
        "format": settings.LOG_FMT_DEV_DEFAULT,
        "dev_mode": False,
    }
    uvicorn_log_config["formatters"]["custom_access"] = {
        "()": UvicornCustomFormatterAccess,
        "format": settings.LOG_FMT_DEV_ACCESS,
        "dev_mode": False,
    }
    uvicorn_log_config["handlers"]["default"]["formatter"] = "custom_default"
    uvicorn_log_config["handlers"]["access"]["formatter"] = "custom_access"
    return uvicorn_log_config


logger = create_logger("backend", dev_mode=False)
uvicorn_log_config = update_uvicorn_log_config()
sys.excepthook = rich_excepthook
