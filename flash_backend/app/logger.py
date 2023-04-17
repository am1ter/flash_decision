import logging
import re
import sys
from copy import deepcopy
from logging import LogRecord
from typing import Any, Literal

import structlog
from structlog.stdlib import LoggerFactory
from uvicorn.config import LOGGING_CONFIG
from uvicorn.logging import AccessFormatter, DefaultFormatter

from .config import settings


class UvicornCustomDefaultFormatter(DefaultFormatter):
    """Custom unicorn logger for system messages"""

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool | None = None,
    ) -> None:
        """Change format for Uvicorn logs to unify it with structlog format"""
        # Source record has format like: [\x1b[32mINFO\x1b[0m:    ]
        self.regex_level = re.compile(r"[0-9]{1,2}m.*[0-9]{1,2}m:")
        self.tags_escape = re.compile(r"\x1b\[([0-9]{1,2})[m]")
        super().__init__(fmt, datefmt, style, use_colors)

    def formatMessage(self, record: LogRecord) -> str:
        record_source = super().formatMessage(record)
        if sys.stdout.isatty():
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
    ) -> None:
        """
        Final access message is a combination of formatted prefix and formatted raw access message
        Prefix formatted with UvicornCustomDefaultFormatter
        """
        fmt_access = fmt.replace(settings.LOG_FMT_DEV_PREF, "") if fmt else None
        self.default_formatter = UvicornCustomDefaultFormatter(settings.LOG_FMT_DEV_PREF)
        self.access_formatter = AccessFormatter(fmt_access)
        super().__init__(fmt, datefmt, style, use_colors)

    def formatMessage(self, record: LogRecord) -> str:
        record_default = self.default_formatter.formatMessage(record)
        record_access = self.access_formatter.formatMessage(record)
        if sys.stdout.isatty():
            return record_default + record_access
        else:
            if record.args and len(record.args) == 5:
                access_args = [arg for arg in record.args if arg]
            else:
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


def create_logger() -> structlog.stdlib.BoundLogger:
    """Create structlog logger"""

    # Set log level and remove extra data from output using format argument
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)

    # Configure structlog
    processors_shared: list[structlog.Processor] = [
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S,%MS", utc=False),
    ]
    processors_mode: list[structlog.Processor]
    if sys.stdout.isatty():
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
    return structlog.get_logger("backend")


def update_uvicorn_log_config() -> dict[str, Any]:
    """Change uvicorn log settings to conform with structlog"""

    uvicorn_log_config = deepcopy(LOGGING_CONFIG)
    uvicorn_log_config["formatters"]["custom_default"] = {
        "()": UvicornCustomDefaultFormatter,
        "format": settings.LOG_FMT_DEV_DEFAULT,
    }
    uvicorn_log_config["formatters"]["custom_access"] = {
        "()": UvicornCustomFormatterAccess,
        "format": settings.LOG_FMT_DEV_ACCESS,
    }
    uvicorn_log_config["handlers"]["default"]["formatter"] = "custom_default"
    uvicorn_log_config["handlers"]["access"]["formatter"] = "custom_access"
    return uvicorn_log_config


logger = create_logger()
uvicorn_log_config = update_uvicorn_log_config()
