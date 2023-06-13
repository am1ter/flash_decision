import logging
import re
import sys
import traceback
from copy import deepcopy
from datetime import datetime
from logging import LogRecord
from pathlib import Path
from site import getsitepackages
from types import TracebackType
from typing import Any, Literal

import attrs
import structlog
from rich import print as rprint
from rich.traceback import Traceback
from structlog.typing import EventDict
from uvicorn.config import LOGGING_CONFIG
from uvicorn.logging import AccessFormatter, DefaultFormatter

from app.system.config import settings


def rich_excepthook(
    type_: type[BaseException], value: BaseException, traceback: TracebackType | None
) -> None:
    """Format exception using rich lib"""

    # To use strings as suppress arguments instead of libs itself, must be used paths to modules
    path_to_libs = getsitepackages()[0]
    suppress = [str(Path(path_to_libs) / Path(s)) for s in settings.SUPPRESS_TRACEBACK_FROM_LIBS]
    rich_tb = Traceback.from_exception(type_, value, traceback, show_locals=True, suppress=suppress)
    rprint(rich_tb)


class UvicornCustomDefaultFormatter(DefaultFormatter):
    """Custom unicorn logger for system messages"""

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool | None = None,
        custom_logger: structlog.stdlib.BoundLogger | None = None,
        dev_mode: bool | None = None,
    ) -> None:
        """Change format for Uvicorn logs to unify it with structlog format"""
        super().__init__(fmt, datefmt, style, use_colors)

        # Source record has format like: [\x1b[32mINFO\x1b[0m:    ] or [INFO:    ]
        regex_pattern = r"[0-9]{1,2}m.*[0-9]{1,2}m:" if self.use_colors else r"(?<=\[)\w+:"
        self.regex_level = re.compile(regex_pattern)
        self.tags_escape = re.compile(r"\x1b\[([0-9]{1,2})[m]")

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

    def __init__(
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
    """
    Custom structlog logger with additional methods and other tweaks.
    Use async calls for everything, but not for the exceptions.
    Async exceptions is not supported by Uvicorn logging.
    """

    dev_mode: bool | None = False

    async def ainfo(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Custom wrapper for logger method (async)"""

        # Show class name
        if kwargs.get("cls") and isinstance(kwargs.get("cls"), type):
            kwargs["cls"] = kwargs["cls"].__name__

        # Convert attrs object to dicts for production mode logs
        if not self.dev_mode and not settings.DEV_MODE:  # type: ignore[attr-defined]
            for kw_key, kw_value in kwargs.items():
                if attrs.has(type(kw_value)):
                    kwargs[kw_key] = attrs.asdict(kw_value, recurse=False)

        # Show the name of the function, where info() called
        if kwargs.get("show_func_name", False):
            del kwargs["show_func_name"]
            callstack_depth = 1  # Extract only last call
            kwargs["function"] = traceback.extract_stack(None, callstack_depth)[0].name

        # Output to logger using async structlog method
        return await super().ainfo(event, *args, **kwargs)

    async def ainfo_finish(self, *args, **kwargs) -> None:
        """To log function/method results"""
        event = "Operation completed"
        await self.ainfo(event, *args, **kwargs)

    def exception(self, event: str | None = None, *args: Any, **kw: Any) -> Any:
        """Use parent logger of wrapped custom logger (sync)"""
        return super().exception(event, *args, **kw)


def create_logger(
    logger_name: str | None = None, dev_mode: bool | None = None
) -> CustomStructlogLogger:
    """Create structlog logger"""

    # Set log level and remove extra data from output using format argument
    logging_level = logging._nameToLevel[settings.LOG_LEVEL]
    logging.basicConfig(level=logging_level, format="%(message)s", stream=sys.stdout)

    # Set dev_mode
    CustomStructlogLogger.dev_mode = dev_mode

    # Configure structlog
    processors_shared: list = [
        structlog.contextvars.merge_contextvars,
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
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=CustomStructlogLogger,
        cache_logger_on_first_use=True,
    )
    logger = structlog.get_logger(logger_name) if logger_name else structlog.get_logger()
    logger.dev_mode = dev_mode
    return logger


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
