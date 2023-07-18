import logging
import re
import sys
import traceback
from contextlib import suppress
from copy import deepcopy
from datetime import datetime
from io import StringIO
from logging import LogRecord
from pathlib import Path
from site import getsitepackages
from types import TracebackType
from typing import Any, Literal, TextIO, cast

import attrs
import structlog
from pythonjsonlogger.jsonlogger import JsonFormatter
from rich import print as rprint
from rich.traceback import Traceback
from structlog.typing import EventDict
from uvicorn.config import LOGGING_CONFIG
from uvicorn.logging import AccessFormatter, DefaultFormatter

from app.system.config import Settings


def rich_excepthook(
    type_: type[BaseException], value: BaseException, traceback: TracebackType | None
) -> None:
    """Format exception using rich lib"""

    # To use strings as suppress arguments instead of libs itself, must be used paths to modules
    libs_path = getsitepackages()[0]
    suppress = [str(Path(libs_path) / Path(s)) for s in Settings().log.SUPPRESS_TRACEBACK_FROM_LIBS]
    try:
        rich_tb = Traceback.from_exception(
            type_, value, traceback, show_locals=True, suppress=suppress
        )
    except Exception:  # noqa: BLE001
        rich_tb = Traceback.from_exception(type_, value, traceback)
    rprint(rich_tb)


class CustomJsonFormatter(JsonFormatter):
    """Custom formatter for production mode for third-party (non-sturctlog) messages"""

    def add_fields(
        self, log_record: dict[str, Any], record: LogRecord, message_dict: dict[str, Any]
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        levelname = log_record.get("levelname")
        assert isinstance(levelname, str)
        if not log_record.get("timestamp"):
            log_record["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        if not log_record.get("levelnumber"):
            log_record["levelnumber"] = logging._nameToLevel[levelname]
            with suppress(KeyError):
                del log_record["level_number"]
        log_record["levelname"] = levelname.lower()


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
        self.logger = custom_logger if custom_logger else structlog.get_logger()

    def formatException(  # type: ignore[override]  # noqa: N802
        self, ei: tuple[type[BaseException], BaseException, TracebackType | None]
    ) -> None:
        """Override exception formatting for uvicorn"""
        if self.dev_mode or Settings().general.DEV_MODE:
            # Use rich print which support suppressing external lib attributes
            rich_excepthook(ei[0], ei[1], ei[2])
        else:
            self.logger.exception(str(ei[1]), exc_info=ei)

    def formatMessage(self, record: LogRecord) -> str:  # noqa: N802
        """Override default formatting method for system logs"""
        record_source = super().formatMessage(record)
        if self.dev_mode or Settings().general.DEV_MODE:
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
                "levelname": record.levelname.lower(),
                "levelnumber": record.levelno,
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
        fmt_access = fmt.replace(Settings().log.LOG_FMT_DEV_PREF, "") if fmt else None
        self.default_formatter = UvicornCustomDefaultFormatter(
            fmt=Settings().log.LOG_FMT_DEV_PREF, dev_mode=dev_mode
        )
        self.access_formatter = AccessFormatter(fmt_access)
        super().__init__(fmt, datefmt, style, use_colors)

        # Force setup dev_mode
        self.dev_mode = dev_mode

    def formatMessage(self, record: LogRecord) -> str:  # noqa: N802
        """Override default formatting method for access logs"""
        record_default = self.default_formatter.formatMessage(record)
        record_access = self.access_formatter.formatMessage(record)
        if self.dev_mode or Settings().general.DEV_MODE:
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
                "levelname": record.levelname.lower(),
                "levelnumber": record.levelno,
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

    def __init__(
        self, *, fmt: str | None = "%Y-%m-%d %H:%M:%S.%f", key: str = "timestamp", utc: bool = False
    ) -> None:
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

    log_text_io: StringIO

    def _process_kwargs(self, kwargs: Any) -> dict[str, Any]:
        # Show class name
        if kwargs.get("cls") and isinstance(kwargs.get("cls"), type):
            kwargs["_cls"] = kwargs["cls"].__name__

        # Convert attrs object to dicts for production mode logs (exclude kwargs with disabled repr)
        if not Settings().general.DEV_MODE:
            for kw_key, kw_value in kwargs.items():
                if not attrs.has(type(kw_value)):
                    continue
                val = attrs.asdict(kw_value, recurse=False, filter=lambda a, _: cast(bool, a.repr))
                kwargs[kw_key] = val

        # Show the name of the function, where info() called
        if kwargs.get("show_func_name", False):
            del kwargs["show_func_name"]
            callstack_depth = 3  # Function where logger was called is on the 3 level of the stack
            kwargs["_function"] = traceback.extract_stack(None, callstack_depth)[0].name

        return kwargs

    async def ainfo(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Custom wrapper for logger method (async)"""
        kwargs_processed = self._process_kwargs(kwargs)
        await super().ainfo(event, *args, **kwargs_processed)

    def info_finish(self, *args, **kwargs) -> None:
        """To log function/method results"""
        event = "Operation completed"
        kwargs_processed = self._process_kwargs(kwargs)
        super().info(event, *args, **kwargs_processed)

    async def ainfo_finish(self, *args, **kwargs) -> None:
        """To log function/method results"""
        event = "Operation completed"
        kwargs_processed = self._process_kwargs(kwargs)
        await super().ainfo(event, *args, **kwargs_processed)

    def error_finish(self, *args, **kwargs) -> None:
        """To log function/method results"""
        event = "Operation completed with errors"
        kwargs_processed = self._process_kwargs(kwargs)
        super().error(event, *args, **kwargs_processed)

    async def aerror_finish(self, *args, **kwargs) -> None:
        """To log function/method results"""
        event = "Operation completed with errors"
        kwargs_processed = self._process_kwargs(kwargs)
        await super().aerror(event, *args, **kwargs_processed)

    def exception(self, event: str | None = None, *args: Any, **kw: Any) -> Any:
        """Use parent logger of wrapped custom logger (sync)"""
        super().exception(event, *args, **kw)


def update_uvicorn_log_config() -> dict[str, Any]:
    """Change uvicorn log settings to conform with structlog"""

    uvicorn_log_config = deepcopy(LOGGING_CONFIG)
    uvicorn_log_config["formatters"]["custom_default"] = {
        "()": UvicornCustomDefaultFormatter,
        "format": Settings().log.LOG_FMT_DEV_DEFAULT,
        "dev_mode": False,
    }
    uvicorn_log_config["formatters"]["custom_access"] = {
        "()": UvicornCustomFormatterAccess,
        "format": Settings().log.LOG_FMT_DEV_ACCESS,
        "dev_mode": False,
    }
    uvicorn_log_config["handlers"]["default"]["formatter"] = "custom_default"
    uvicorn_log_config["handlers"]["access"]["formatter"] = "custom_access"
    return uvicorn_log_config


def configure_logger(dev_mode: bool | None = None, stream: StringIO | TextIO = sys.stdout) -> None:
    """Set global log level and configure structlog for dev and prod mode"""

    processors_shared: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        CustomTimeStamper(),
    ]
    processors_dev_structlog_only: list = [structlog.stdlib.ProcessorFormatter.wrap_for_formatter]
    processors_dev_third_party: list = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,  # Remove meta info
        structlog.dev.ConsoleRenderer(),
    ]
    processors_prod: list = [
        structlog.processors.add_log_level,
        CustomTimeStamper(),
        structlog.stdlib.add_log_level_number,
        structlog.processors.dict_tracebacks,
        structlog.stdlib.render_to_log_kwargs,
    ]

    logging_level = logging._nameToLevel[Settings().log.LOG_LEVEL]
    logging.basicConfig(level=logging_level, format="%(message)s")
    root_logger = logging.getLogger()
    root_logger.handlers = []  # Remove default root logger handler
    root_logger.setLevel(logging_level)
    handler = logging.StreamHandler(stream=stream)
    formatter_mode: logging.Formatter
    if Settings().general.DEV_MODE or dev_mode:
        processors_mode = processors_dev_structlog_only
        formatter_mode = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=processors_shared,  # For third-party messages (non-structlog)
            processors=processors_dev_third_party,  # For all messages after the pre_chain is done
        )
    else:
        processors_mode = processors_prod
        formatter_mode = CustomJsonFormatter(fmt="%(timestamp)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter_mode)
    root_logger.addHandler(handler)
    structlog.configure(
        processors=processors_shared + processors_mode,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=CustomStructlogLogger,
        cache_logger_on_first_use=True,
    )
    sys.excepthook = rich_excepthook
